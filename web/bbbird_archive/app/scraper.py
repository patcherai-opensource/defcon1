from app import app

import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
import subprocess
import tempfile
import os
import uuid
import shutil
from pathlib import Path
from urllib.parse import urlparse

import ipaddress
import socket

import logging
logging.basicConfig()
logging.getLogger(__name__)

class ScrapeError(Exception):
    pass

ALLOWED_SCHEMES = ["http", "https"]
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local / cloud metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10")
]

def _validate_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ScrapeError(f"Unsupported URL scheme: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ScrapeError("URL has no hostname")
   
    try:
        resolved = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        raise ScrapeError(f"Cannot resolve hostname: {hostname}")
    
    for family, _, _, _, sockaddr in resolved:
        ip = ipaddress.ip_address(sockaddr[0])

        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
        
        for network in BLOCKED_NETWORKS:
            if ip in network:
                raise ScrapeError("Access to private/internal addresses is not allowed")
    
    return parsed

def _fetch(url, auth_user, auth_pass):
    try:
        r = requests.get(url, allow_redirects=False)
        if r.status_code == 401:
            r.close()
            auth_header = r.headers.get("WWW-Authenticate", "").lower()
            if "basic" in auth_header:
                r = requests.get(url, auth=HTTPBasicAuth(auth_user, auth_pass), allow_redirects=False)
            elif "digest" in auth_header:
                r = requests.get(url, auth=HTTPDigestAuth(auth_user, auth_pass), allow_redirects=False)
            else:
                raise ScrapeError(f"Unsupported auth method {auth_header}")
        r.raise_for_status()
        return r
    except requests.ConnectionError:
        raise ScrapeError("Could not connect to the server. Check the URL and try again.")
    except requests.Timeout:
        raise ScrapeError("The request timed out. The server took too long to respond.")
    except requests.HTTPError as e:
        code = e.response.status_code if e.response is not None else None
        friendly = {
            403: "Access denied - the server refused the request.",
            404: "Image not found - the URL may be wrong or the image was removed.",
            500: "The remote server encountered an error.",
            502: "The remote server returned a bad gateway error.",
            503: "The remote server is temporarily unavailable.",
        }
        raise ScrapeError(friendly.get(code, f"The server returned an error (HTTP {code})."))
    except requests.RequestException:
        raise ScrapeError("Something went wrong while fetching the image. Check the URL and try again.")
    
def scrape(url, auth_user, auth_pass):
    _validate_url(url)
    
    r = _fetch(url, auth_user, auth_pass)
    
    content_type = r.headers.get("Content-Type", "")
    ext = MIMETYPE_TO_EXT.get(content_type)
    if not ext:
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix
        
    tmp = tempfile.NamedTemporaryFile(delete=False, dir=app.config["UPLOAD_FOLDER"], suffix=ext)
    
    max_content_size = app.config["MAX_CONTENT_SIZE"]
    
    content_length = int(r.headers.get("Content-Length", 0))
    if content_length > max_content_size:
        raise ScrapeError(
            f"File exceeds max allowed size {content_length}"
        )
    
    try:
        downloaded = 0
        for chunk in r.iter_content(chunk_size=65536):
            downloaded += len(chunk)
            if downloaded > max_content_size:
                raise ScrapeError("Download exceeded max allowed size")
            tmp.write(chunk)
        tmp.close()
        r.close()

        meta = verify(tmp.name)
        if meta is None:
            raise ScrapeError("Image verification failed")

        ext = IMAGEMAGICK_FORMAT_TO_EXT.get(meta["format"].upper(), ext)
        safe_name = f"{uuid.uuid4().hex}{ext}"
        dest = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
        shutil.move(tmp.name, dest)

        meta["file_size"] = os.path.getsize(dest)
        return safe_name, meta

    except Exception:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        raise


def verify(filepath):
    try:
        result = subprocess.run(["identify", "-format", "%w %h %m", "--", filepath], capture_output=True)
    except subprocess.TimeoutExpired:
        raise ScrapeError("Image verification timed out")
   
    if result.returncode != 0:
        raise ScrapeError("Image verification failed")
    
    try:
        raw = result.stdout.strip()
        (width, height, fmt) = raw.split(b" ")
    except ValueError:
        raise ScrapeError(f"Could not parse ImageMagick output: {raw.decode('utf-8', errors='replace')}")

    return {
        "width": int(width.decode('utf-8')),
        "height": int(height.decode('utf-8')),
        "format": fmt.decode('utf-8'),
    }
    
MIMETYPE_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "image/tiff": ".tif",
    "image/heic": ".heif",
    "image/avif": ".avif"
}

IMAGEMAGICK_FORMAT_TO_EXT = {
    "JPEG": ".jpg",
    "JPG": ".jpg",
    "PNG": ".png",
    "PNG8": ".png",
    "PNG24": ".png",
    "PNG32": ".png",
    "PNG48": ".png",
    "PNG64": ".png",
    "GIF": ".gif",
    "GIF87": ".gif",
    "WEBP": ".webp",
    "BMP": ".bmp",
    "BMP2": ".bmp",
    "BMP3": ".bmp",
    "TIFF": ".tif",
    "TIFF64": ".tif",
    "TIF": ".tif",
    "ICO": ".ico",
    "CUR": ".cur",
    "TGA": ".tga",
    "PSD": ".psd",
    "HEIC": ".heic",
    "HEIF": ".heif",
    "AVIF": ".avif",
    "EXR": ".exr",
    "HDR": ".hdr",
    "DPX": ".dpx",
    "JP2": ".jp2",
}