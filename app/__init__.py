from flask import Flask
import psycopg2
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "secret"
app.permanent_session_lifetime = timedelta(hours=1)


from app import routes
