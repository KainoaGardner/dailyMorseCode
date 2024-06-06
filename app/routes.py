from flask import redirect, url_for, render_template, flash, session, request
import psycopg2
from app import app
from app.db import *
from app.other import getDBSize, getTodayIndex, getEntry, encrypt, decrypt


@app.route("/", methods=["GET", "POST"])
def home():
    dbSize = getDBSize()
    todayIndex = getTodayIndex()
    todayIndex = todayIndex % dbSize

    entry = getEntry(todayIndex)
    text = encrypt(entry[0])
    author = encrypt(entry[1])
    result = ""
    textAnswer = ""
    authorAnswer = ""

    if request.method == "POST":
        textAnswer = decrypt(text)
        authorAnswer = decrypt(author)
        textInput = request.form["text"].upper()
        authorInput = request.form["author"].upper()

        if textInput == textAnswer and authorAnswer == authorAnswer:
            result = "Correct"
        elif textInput == textAnswer:
            result = "IncorrectAuthor"
        elif authorInput == authorAnswer:
            result = "IncorrectText"
        else:
            result = "IncorrectBoth"

    return render_template(
        "home.html",
        text=text,
        author=author,
        textAnswer=textAnswer,
        authorAnswer=authorAnswer,
        result=result,
    )


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/test")
def test():

    # print(encrypt("test"))
    # print(decrypt(".... . -. .-. -.-- / ..-. --- .-. -.. "))
    session.pop("todayIndex", None)
    session.pop("dbSize", None)
    session.pop("message", None)
    return redirect(url_for("home"))


@app.route("/admin")
def admin():
    with db_cursor() as cur:
        cur.execute("SELECT * FROM text")
        entries = cur.fetchall()

    return render_template("admin.html", entries=entries)
