import sqlite3
from flask import current_app, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

mail = Mail()

def initDB():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fName TEXT NOT NULL,
                        lName TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        username TEXT NOT NULL UNIQUE,
                        displayName TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'user',
                        icon TEXT NOT NULL DEFAULT 'Kset.png',
                        verified BOOLEAN NOT NULL DEFAULT 0,
                        verifiedAt DATETIME
                    )''')
    conn.commit()
    conn.close()

def generateConfirmationToken(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirmation-salt')

def verifyConfirmationToken(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.loads(token, salt='email-confirmation-salt', max_age=3600)

def sendConfirmationEmail(userEmail):
    token = generateConfirmationToken(userEmail)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    msg = Message('Please confirm your email', recipients=[userEmail])
    msg.body = f"Click to confirm your email: {confirm_url}"
    mail.send(msg)
