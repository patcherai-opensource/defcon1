from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes
from app import db

@app.cli.command("init-db")
def init_db_command():
    db.init_db()
    print("Database initialized.")