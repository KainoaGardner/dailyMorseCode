from flask import redirect, url_for, render_template, flash, session, request
from sqlalchemy import select
from datetime import date, timedelta
from app import app, db
from app.tables import User, Quote, Answer
from app.quotes import quotes
from app.other import getTodayIndex, encrypt, decrypt


@app.route("/setup_home")
def setup_home():
    session.pop("input", None)
    return redirect(url_for("home"))


@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    userId = session["user"]["id"]
    answered = Answer.query.filter_by(user_id=userId, date=date.today()).first()
    if answered:
        return redirect(url_for("answered"))

    dbSize = db.session.query(Quote).count()
    todayIndex = getTodayIndex()
    todayIndex = todayIndex % dbSize

    entry = Quote.query.get(todayIndex)
    text = encrypt(entry.text)
    author = encrypt(entry.author)

    session["quote"] = {
        "quote": {"text": entry.text, "author": entry.author},
        "encrypt": {"text": text, "author": author},
    }
    result = ""
    textAnswer = ""
    authorAnswer = ""

    if request.method == "POST":
        textAnswer = decrypt(text)
        authorAnswer = decrypt(author)
        textInput = request.form["text"].upper()
        authorInput = request.form["author"].upper()
        session["input"] = {"quote": textInput, "author": authorInput}

        if textInput == textAnswer and authorAnswer == authorAnswer:
            result = "Correct"
            answer = Answer(date.today(), todayIndex, userId)
            db.session.add(answer)
            db.session.commit()
            return redirect(url_for("result"))
        elif textInput == textAnswer:
            result = "Author Incorrect"
        elif authorInput == authorAnswer:
            result = "Text Incorrect"
        else:
            result = "Both Incorrect"

    if "input" in session:
        input = session["input"]
    else:
        input = None

    return render_template(
        "home.html",
        text=text,
        author=author,
        textAnswer=textAnswer,
        authorAnswer=authorAnswer,
        result=result,
        input=input,
    )


@app.route("/answered")
def answered():
    quote = session["quote"]
    return render_template("answered.html", quote=quote)


@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST":
        return redirect(url_for("home"))
    quote = session["quote"]

    return render_template("result.html", quote=quote)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        user = session["user"]
        flash(f"{user["username"]} is already logged in")
        return redirect(url_for("user"))
    else:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session["user"] = {"username": user.username, "id": user.id}
                flash(f"You have been logged in as {user.username}")
                return redirect(url_for("user"))

            else:
                flash(f"There is no user with that information")
                return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    user = session["user"]
    session.pop("user", None)
    flash(f"{user["username"]} has been logged out")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user:
            flash(f"The username {username} is already taken")
            return redirect(url_for("register"))
        else:
            flash(f"{username} has been registered")
            user = User(username, password, date.today())
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/user")
def user():
    if "user" not in session:
        return redirect(url_for("login"))

    user = session["user"]

    answered = Answer.query.filter_by(user_id=user["id"]).all()

    temp_date = date.today()
    days_in_row = 0
    while temp_date in answered:
        days_in_row += 1
        temp_date = date.today() - timedelta(1)

    total_answered = len(answered)

    return render_template(
        "user.html", user=user, total_answered=total_answered, days_in_row=days_in_row
    )


@app.route("/test")
def test():
    return "hello"


@app.route("/admin")
def admin():

    all_users = user.query.all()
    all_answers = answer.query.all()
    all_quotes = quote.query.all()

    return render_template(
        "admin.html",
        all_users=all_users,
        all_quotes=all_quotes,
        all_answers=all_answers,
    )


@app.route("/database")
def createdatabase():
    for quote in quotes:
        entry = quote(quote["quote"], quote["author"])
        db.session.add(entry)

    db.session.commit()
    return redirect(url_for("admin"))


@app.route("/resetstats")
def resetstats():
    user = session["user"]
    db.session.query(Answer).filter_by(user_id=user["id"]).delete()
    db.session.commit()

    return redirect(url_for("user"))


@app.route("/emptyusers")
def emptyusers():
    db.session.query(user).delete()
    db.session.commit()
    return redirect(url_for("admin"))
