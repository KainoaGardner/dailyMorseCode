from flask import session
from datetime import date

from app.morse import letterToMorse, morseToLetter


def getTodayIndex():
    today = str(date.today())

    year = int(today[0:4])
    month = int(today[5:7])
    day = int(today[8:])

    number = year * 365 + month * 12 * day
    return number


def encrypt(text):
    result = ""
    text = text.upper()
    for i in range(len(text)):
        if text[i] in letterToMorse:
            result += letterToMorse[text[i]] + " "
        elif text[i] == " ":
            result += " / "

    return result


def decrypt(text):
    result = ""
    text = text.split("/")
    for word in text:
        for letter in word.split(" "):
            if letter in morseToLetter:
                result += morseToLetter[letter]

        result += " "

    return result[:-1]
