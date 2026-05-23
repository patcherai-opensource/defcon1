import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))
    FLAG = os.environ.get("FLAG", "bbb{hihellotestflag}")
    
    BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME", "")
    BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD", "")
    
    DB_SERVER = os.environ.get("DB_SERVER", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 1433))
    DB_DATABASE = os.environ.get("DB_DATABASE", "birdarchive")
    DB_USER = os.environ.get("DB_USERNAME", "babelfish_user")
    DB_PASSWORD = "12345678"
    
    UPLOAD_FOLDER     = os.path.join(os.path.dirname(__file__), "app","static", "scraped")
    MAX_CONTENT_SIZE  = 20 * 1024 * 1024  # 20 MB download limit
    REQUEST_TIMEOUT   = 600                # seconds for HTTP fetch
    MAX_FORM_MEMORY_SIZE = 20 * 1024 * 1024