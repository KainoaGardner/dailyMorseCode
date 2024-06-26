from flask import redirect, url_for, render_template, flash, session, request
from sqlalchemy import select
from datetime import date, datetime
from app import app, db
from app.tables import User, Quote, Answer
from app.quotes import quotes
from app.other import getTodayIndex, encrypt, decrypt, get_streak


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

    today_date = date.today()
    return render_template(
        "home.html",
        text=text,
        author=author,
        textAnswer=textAnswer,
        authorAnswer=authorAnswer,
        result=result,
        input=input,
        date=today_date,
    )


@app.route("/answered")
def answered():
    if "quote" not in session:

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

    quote = session["quote"]
    today_date = date.today()

    return render_template("answered.html", quote=quote, date=today_date)


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

    answered = (
        Answer.query.with_entities(Answer.date).filter_by(user_id=user["id"]).all()
    )

    user_db = User.query.filter_by(username=user["username"]).first()
    days_in_row = get_streak(answered)
    user_db.answers_in_row = max(days_in_row, user_db.answers_in_row)
    db.session.commit()

    total_answered = len(answered)

    return render_template(
        "user.html",
        user=user,
        total_answered=total_answered,
        days_in_row=days_in_row,
        max_day_in_row=user_db.answers_in_row,
    )


@app.route("/setup_convert")
def setup_convert():
    session.pop("convert_input", None)
    session.pop("convert_type", None)
    session.pop("converted", None)
    return redirect(url_for("convert"))


@app.route("/convert", methods=["GET", "POST"])
def convert():
    if "convert_type" not in session:
        session["convert_type"] = 0

    if request.method == "POST":
        if "convert_type" in request.form:
            if session["convert_type"] == 0:
                session["convert_type"] = 1
            else:
                session["convert_type"] = 0
            session.pop("convert_input", None)
            session.pop("converted", None)
            return redirect(url_for("convert"))

        elif "convert_submit" in request.form:
            text = request.form["convert_text"]
            if session["convert_type"] == 0:
                result = encrypt(text)
            else:
                result = decrypt(text)

            session["converted"] = result
            session["convert_input"] = text
            return redirect(url_for("convert"))

    if "converted" in session:
        converted = session["converted"]
    else:
        converted = ""

    if "convert_input" in session:
        convert_input = session["convert_input"]
    else:
        convert_input = ""

    return render_template(
        "convert.html",
        converted=converted,
        convert_type=session["convert_type"],
        convert_input=convert_input,
    )


@app.route("/test")
def test():
    return "hello"


@app.route("/admin")
def admin():

    all_users = User.query.all()
    all_answers = Answer.query.all()
    all_quotes = Quote.query.all()

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
    db.session.query(User).delete()
    db.session.commit()
    return redirect(url_for("admin"))
