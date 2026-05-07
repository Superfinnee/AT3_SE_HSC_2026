from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import os
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

def initDB():
    conn = sqlite3.connect('TfNSW.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fName TEXT NOT NULL,
                        lName TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        username TEXT NOT NULL UNIQUE,
                        displayName TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'user'
                        icon TEXT NOT NULL DEFAULT 'Kset.png'
                    )''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            fName = escape(request.form['fName'])
            lName = escape(request.form['lName'])
            email = escape(request.form['email'])
            username = escape(request.form['username'])
            displayName = escape(request.form['displayName'])
            password = escape(request.form['password'])
            confirmPassword = escape(request.form['confirmPassword'])

            if password != confirmPassword:
                flash("Passwords do not match.", "error")
                return redirect(url_for('register'))

            if not fName or not lName or not email or not username or not displayName or not password:
                flash("All fields are required.", "error")
                return redirect(url_for('register'))

            conn = sqlite3.connect('TfNSW.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT email, username, displayName FROM users WHERE email = ? OR username = ? OR displayName = ?', (email, username, displayName))
            results = cursor.fetchone()
            
            if results:
                existingEmail = results[0]
                existingUsername = results[1]
                existingDisplayName = results[2]

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

            
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('register'))

        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            usernameOrEmail = escape(request.form['username'])
            password = escape(request.form['password'])

            conn = sqlite3.connect('TfNSW.db')
            cursor = conn.cursor()
            cursor.execute('SELECT password, username, ID, status, icon FROM users WHERE username = ? OR email = ?', (usernameOrEmail, usernameOrEmail))
            result = cursor.fetchone()
            conn.close()

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
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)