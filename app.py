from flask import Flask, request, redirect, url_for, flash, render_template
import sqlite3

app = Flask(__name__)
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
app.secret_key = os.urandom(24)

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
    user = conn.execute("SELECT * FROM Users_info WHERE (Username=? OR Email_ID=?) AND Password=?",
                        (email, email, password)).fetchone()
    conn.close()

    if user:
        flash("Login successful!", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('home'))

@app.route('/forgetPassword', methods=['POST'])
def forget_password():
    email = request.form['email']

    conn = get_db_connection()
    user = conn.execute("SELECT Password FROM Users_info WHERE Email_ID=?", (email,)).fetchone()

    if user:
        password = user["Password"]
        # Here you would send the password to the user's email or handle password reset logic
    conn.close()

    flash("If the email exists, instructions have been sent.", "info")
    return redirect(url_for('home'))

@app.route('/sendPassword', methods=['POST'])
def send_password():
        email = request.form['email']

        conn = get_db_connection()
        user = conn.execute("SELECT Password FROM Users_info WHERE Email_ID=?", (email,)).fetchone()
        conn.close()

        if user:
            password = user["Password"]
            # Email configuration
            sender_email = "your_email@example.com"
            sender_password = "your_email_password"
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
                flash("Failed to send email. Please try again later.", "danger")
        else:
            flash("Email not found.", "danger")

        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
