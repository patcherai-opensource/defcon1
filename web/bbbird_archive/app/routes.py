from flask import render_template, request, redirect, url_for, Response, flash
from app import app
from app import scraper, db

def check_auth(username, password):
    return username == app.config["BASIC_AUTH_USERNAME"]  and password == app.config["BASIC_AUTH_PASSWORD"]

@app.before_request
def require_basic_auth():
    # Skip is basic auth isn't configured
    if not app.config["BASIC_AUTH_USERNAME"] or not app.config["BASIC_AUTH_PASSWORD"]:
        return
    
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return Response('Unauthorized', 401,
                        {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route("/")
def index():
    try:
        images = db.get_images()
    except Exception:
        images = []
    try:
        flags = db.get_flags()
    except Exception as e:
        flags = []
    return render_template("index.html", images=images, flags=flags)

@app.route("/scrape", methods=["POST"])
def scrape():
    url = request.form.get("url", "").strip()
    if not url:
        flash("Please enter a URL.", "error")
        return redirect(url_for("index"))
    
    auth_user = request.form.get("username", "").strip()
    auth_pass = request.form.get("password", "").strip()
        
    if not url.startswith(("http://", "https://")):
        flash("URL must start with http:// or https://.", "error")
        return redirect(url_for("index"))
        
    try:
        (safe_name, meta) = scraper.scrape(url, auth_user, auth_pass)
    except scraper.ScrapeError as e:
        flash(f"Failed to scrape image: {e}", "error")
        return redirect(url_for("index"))

    try:
        db.insert_image(url, safe_name, meta)
    except Exception as e:
        flash(f"Image scraped but failed to save: {e}", "error")
        print(f"DB insert failed: {e}")
    
    return redirect(url_for("index"))

