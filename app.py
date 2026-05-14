from flask import Flask, render_template, request, redirect, session, url_for, flash, current_app
import sqlite3
from dotenv import load_dotenv
load_dotenv()
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from extensions import mail, initDB, verifyConfirmationToken, sendConfirmationEmail

app = Flask(__name__)
app.config.from_object(Config)
mail.init_app(app)

with app.app_context():
    initDB()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        fName = escape(request.form['fName'])
        lName = escape(request.form['lName'])
        email = escape(request.form['email'])
        username = escape(request.form['username'])
        displayName = escape(request.form['displayName'])
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        if password != confirmPassword:
            flash("Passwords do not match.", "error")
            return redirect(url_for('register'))

        if not fName or not lName or not email or not username or not displayName or not password or not confirmPassword:
            flash("All fields are required.", "error")
            return redirect(url_for('register'))

        conn = sqlite3.connect(current_app.config['DATABASE'])
        cursor = conn.cursor()

        cursor.execute('SELECT email, username, displayName FROM users WHERE email = ? OR username = ? OR displayName = ?', (email, username, displayName))
        results = cursor.fetchone()

        if results:
            existingEmail = results[0]
            existingUsername = results[1]
            existingDisplayName = results[2]
        else:
            existingEmail = None
            existingUsername = None
            existingDisplayName = None

        if existingEmail == email:
            flash("Email already exists. Please choose a different email.", "error")
            conn.close()
            return redirect(url_for('register'))
        if existingUsername == username:
            flash("Username already exists. Please choose a different username.", "error")
            conn.close()
            return redirect(url_for('register'))
        if existingDisplayName == displayName:
            flash("Display name already exists. Please choose a different display name.", "error")
            conn.close()
            return redirect(url_for('register'))

        #Is this something I should turn into a function?
        if len(fName) > 50:
            flash("First name is too long.", "error")
            conn.close()
            return redirect(url_for('register'))
        if len(lName) > 50:
            flash("Last name is too long.", "error")
            conn.close()
            return redirect(url_for('register'))
        if len(email) > 100:
            flash("Email is too long.", "error")
            conn.close()
            return redirect(url_for('register'))
        if len(username) > 50:
            flash("Username is too long.", "error")
            conn.close()
            return redirect(url_for('register'))
        if len(displayName) > 30:
            flash("Display name is too long.", "error")
            conn.close()
            return redirect(url_for('register'))

        cursor.execute('INSERT INTO users (fName, lName, email, username, displayName, password) VALUES (?, ?, ?, ?, ?, ?)',
                    (fName, lName, email, username, displayName, generate_password_hash(password)))
        conn.commit()
        conn.close()

        sendConfirmationEmail(email)

        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        usernameOrEmail = escape(request.form['usernameOrEmail'])
        password = request.form['password']

        conn = sqlite3.connect(current_app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('SELECT password, username, id, status, icon, verified FROM users WHERE username = ? OR email = ?', (usernameOrEmail, usernameOrEmail))
        result = cursor.fetchone()
        conn.close()

        if result and result[5] == 0:
            flash("Please confirm your email before logging in.", "error")
            return redirect(url_for('login'))
        elif not result:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

        if result and check_password_hash(result[0], password):
            flash("Login successful!", "success")
            session['userID'] = result[2]
            session['username'] = result[1]
            session['status'] = result[3]
            session['icon'] = result[4]
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/')
def index():
    if 'userID' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = verifyConfirmationToken(token)
    except Exception:
        flash("The confirmation link is invalid or has expired.", "error")
        return redirect(url_for('login'))

    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET verified = 1, verifiedAt = CURRENT_TIMESTAMP WHERE email = ?', (email,))
    conn.commit()
    conn.close()

    flash("Email confirmed! You can now log in.", "success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
