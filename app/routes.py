from flask import redirect, url_for, render_template, flash
import psycopg2

from app import app
from app.db import *


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/admin")
def admin():
    with db_cursor() as cur:
        cur.execute("SELECT * FROM text")
        entries = cur.fetchall()

    return render_template("admin.html", entries=entries)
