from flask import Flask, request, redirect, url_for, flash, render_template, session
import sqlite3

from api.stocks_api import stocks_bp

app = Flask(__name__)
app.register_blueprint(stocks_bp, url_prefix="/api/stocks")

import os
from dotenv import load_dotenv

load_dotenv()
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
app.secret_key = os.urandom(24)

@app.route("/")
def intro():
    return render_template("logo.html")

@app.route("/loading")
def loading():
    return render_template("loading_page.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/home")
def home():
    conn = sqlite3.connect("stock_game.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT Username,Balance FROM Users_info where id=?",(session["user_id"],))

    users = cur.fetchone()
    conn.close()
    # If user logged in, hide forms on the page by sending show_forms=False
    show_forms = "user" not in session
    return render_template("home_page.html", show_forms=show_forms, user=users)

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
    password = request.form['password']

    conn = get_db_connection()
    try:
        cursor = conn.execute("INSERT INTO Users_info (First_Name, Last_Name, Username, Email_ID, Password) VALUES (?, ?, ?, ?, ?)",
                     (first_name, last_name, username, email, password))
        conn.commit()
        # log the user in immediately after sign up
        user_id = cursor.lastrowid
        session['user_id'] = user_id
        session['user'] = username
        flash("Account created successfully. You are now logged in.", "success")
        return redirect(url_for('home'))
    except Exception as e:
        flash("Error: Username or Email already exists.", "danger")
        return redirect(url_for('form'))
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM Users_info WHERE Email_ID=? AND Password=?",
                        (email, password)).fetchone()
    conn.close()

    if user:
        # mark user as logged in
        session['user_id'] = user['id']
        session['user'] = user['Username']
        flash("Login successful!", "success")
        return redirect(url_for('home'))   # redirect to home where forms are hidden
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('form'))


@app.route('/forgetPassword', methods=['POST'])
def forget_password():
    email = request.form['email']

    conn = get_db_connection()
    user = conn.execute("SELECT Password FROM Users_info WHERE Email_ID=?", (email,)).fetchone()
    conn.close()

    if user:
        password = user["Password"]

        sender_email = os.getenv("EMAIL_USER")
        sender_password = os.getenv("EMAIL_PASS")
        receiver_email = email

        subject = "Your Password for Stock Exchange Game"
        body = f"Your password is: {password}"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())

            flash("Password sent to your email.", "success")
        except Exception as e:
            flash(f"Failed to send email: {str(e)}", "danger")

    else:
        flash("Email not found.", "danger")

    return redirect(url_for('form'))


@app.route('/leaderboard')
def leaderboard(): 
    leaderboard_data = get_leaderboard()

    return render_template("leaderBoard.html", leaderboard=leaderboard_data)

def get_leaderboard():
    conn = get_db_connection()
    rows = conn.execute("""
    SELECT
        Username,
        Portfolio_value,
        Balance,
        (Portfolio_value + Balance) AS Net_Worth
    FROM Users_info
    ORDER BY Net_Worth DESC
    LIMIT 10
""").fetchall()
    conn.close()
    return rows

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/privacy")
def privacy():
    return render_template("privacyPolicy.html")




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

