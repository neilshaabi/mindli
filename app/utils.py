from flask import render_template, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer


def isValidPassword(password: str) -> bool:
    """
    Returns whether a given password meets the security requirements
    (at least 8 characters with at least one digit, one uppercase letter
    and one lowercase letter)"""
    if (
        (len(password) < 8)
        or (not any(char.isdigit() for char in password))
        or (not any(char.isupper() for char in password))
        or (not any(char.islower() for char in password))
    ):
        return False
    else:
        return True


def sendEmailWithToken(
    s: URLSafeTimedSerializer, mail: Mail, name: str, email: str, subject: str
) -> None:
    """Sends an email with a token-generated link"""
    # Generate email contents based on subject
    token = s.dumps(email)
    msgInfo = getMsg(token, subject)

    msg = Message(subject, recipients=[email])
    msg.html = render_template(
        "email.html",
        name=name,
        body=msgInfo[0],
        btn_link=msgInfo[1],
        btn_text=msgInfo[2],
    )
    mail.send(msg)
    return


# Returns a dictionary with text to include in an email depending on the subject
def getMsg(token, subject: str):
    return ""
    link = url_for(route, token=token, _external=True)
    return [body, link, btn_text]
