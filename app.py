from flask import Flask, request, redirect, url_for, flash, render_template
import sqlite3

app = Flask(__name__)
import os
app.secret_key = "os.urandom(24)"

@app.route("/home")
def home():
    return render_template("home_page.html")

def get_db_connection():
    conn = sqlite3.connect('stock_game.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/signUp', methods=['POST'])
def signup():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['Username']
    email = request.form['email']
    password = request.form['password']   # You should hash this!

    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO Users_info (First_Name, Last_Name, Username, Email_ID, Password) VALUES (?, ?, ?, ?, ?)",
                     (first_name, last_name, username, email, password))
        conn.commit()
        flash("Account created successfully. Please login.", "success")
    except:
        flash("Error: Username or Email already exists.", "danger")
    finally:
        conn.close()

    return redirect(url_for('home'))  # or wherever you want to go after signup


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?",
                        (email, password)).fetchone()
    conn.close()

    if user:
        flash("Login successful!", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('home'))

@app.route('/forgetPassword', methods=['POST'])
def forgot_password():
    email = request.form['email']
    new_password = "123456"  # Or generate a random one

    conn = get_db_connection()
    conn.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
    conn.commit()
    conn.close()

    flash("New password set. Please check your email.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)