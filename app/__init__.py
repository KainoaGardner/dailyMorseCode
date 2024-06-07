from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "secret"
app.permanent_session_lifetime = timedelta(hours=1)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:root@localhost:5432/flask_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from app import routes
