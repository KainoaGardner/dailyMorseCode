from app import db
from app.quotes import quotes


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    registerDate = db.Column(db.Date)
    answers_in_row = db.Column(db.Integer)
    answer = db.relationship("Answer")

    def __init__(self, username, password, date):
        self.username = username
        self.password = password
        self.registerDate = date
        self.answers_in_row = 0


class Answer(db.Model):
    __tablename__ = "answer"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    answer_id = db.Column(db.ForeignKey("quote.id"))
    user_id = db.Column(db.ForeignKey("users.id"))

    def __init__(self, date, answer_id, user_id):
        self.date = date
        self.answer_id = answer_id
        self.user_id = user_id


class Quote(db.Model):
    __tablename__ = "quote"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), unique=True)
    author = db.Column(db.String(100))
    answer = db.relationship("Answer")

    def __init__(self, text, author):
        self.text = text
        self.author = author
