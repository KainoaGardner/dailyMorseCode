from flask import redirect, url_for, render_template, flash, session, request
from sqlalchemy import select
from datetime import date
from app import app, db
from app.tables import User, Quote, Answer
from app.quotes import quotes
from app.other import getTodayIndex, encrypt, decrypt


@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    dbSize = db.session.query(Quote).count()
    todayIndex = getTodayIndex()
    todayIndex = todayIndex % dbSize

    entry = Quote.query.get(todayIndex)
    text = encrypt(entry.text)
    author = encrypt(entry.author)
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("user"))
    else:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session["user"] = user.username
                return redirect(url_for("user"))

            else:
                return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user:
            return redirect(url_for("register"))
        else:
            user = User(username, password, date.today())
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/user")
def user():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("user.html", user=user)


@app.route("/test")
def test():

    return "hello"


@app.route("/admin")
def admin():

    all_users = User.query.all()

    return render_template("admin.html", all_users=all_users)


@app.route("/database")
def createDatabase():
    for quote in quotes:
        entry = Quote(quote["quote"], quote["author"])
        db.session.add(entry)

    db.session.commit()
    return redirect(url_for("admin"))


@app.route("/resetStats")
def resetStats():
    session.pop("user", None)
    return redirect(url_for("user"))


@app.route("/emptyUsers")
def emptyUsers():
    db.session.query(User).delete()
    db.session.commit()
    return redirect(url_for("admin"))
