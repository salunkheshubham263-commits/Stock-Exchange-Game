from flask import Flask, request, redirect, url_for, flash, render_template, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlcipher3 import dbapi2 as sqlite3
from api.stocks_api import stocks_bp
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

app = Flask(__name__)
app.register_blueprint(stocks_bp, url_prefix="/api/stocks")
app.secret_key = os.getenv("Flask_secret_key")

# -------------------- DATABASE CONNECTION --------------------
def get_db_connection():
    conn = sqlite3.connect("stock_game.db")
    conn.execute(f"PRAGMA key='{os.getenv('secret_key')}'")  # Set encryption key
    conn.row_factory = sqlite3.Row
    return conn

# -------------------- ROUTES --------------------
@app.route("/")
def intro():
    return render_template("logo.html")

@app.route("/loading")
def loading():
    return render_template("loading_page.html")

@app.route("/privacy")
def privacy():
    return render_template("PrivacyPolicy.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/home")
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT Username, Balance FROM Users_info WHERE id=?", (session.get("user_id"),))
        user = cur.fetchone()
    finally:
        conn.close()

    show_forms = "user" not in session
    return render_template("home_page.html", show_forms=show_forms, user=user)

# -------------------- USER SIGNUP & LOGIN --------------------
@app.route('/signUp', methods=['POST'])
def signup():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['Username']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO Users_info (First_Name, Last_Name, Username, Email_ID, Password) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, username, email, hashed_password)
        )
        conn.commit()
        user_id = cursor.lastrowid
        session['user_id'] = user_id
        session['user'] = username
        flash("Account created successfully. You are now logged in.", "success")
        return redirect(url_for('home'))
    except Exception:
        flash("Error: Username or Email already exists.", "danger")
        return redirect(url_for('form'))
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT * FROM Users_info WHERE Email_ID=?",
            (email,)
        ).fetchone()
    finally:
        conn.close()

    if user and check_password_hash(user["Password"], password):
        session['user_id'] = user['id']
        session['user'] = user['Username']
        flash("Login successful!", "success")
        return redirect(url_for('home'))
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('form'))

# -------------------- FORGOT PASSWORD --------------------
import random
import string
import threading
import requests

def send_email_resend(to_email, temp_password):
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {os.getenv('RESEND_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Stock Game <onboarding@resend.dev>",
                "to": [to_email],
                "subject": "Stock Exchange Game - Password Reset",
                "html": f"""
                    <h2>Password Reset</h2>
                    <p>Your temporary password is:</p>
                    <h1>{temp_password}</h1>
                    <p>Login and change it immediately.</p>
                    <p>You can change your password in the Account section after logging in.</p>
                    <p>If you did not request this, ignore this email.</p>
                """
            }
        )

        print("Resend status:", response.status_code)
        print("Resend response:", response.text)

    except Exception as e:
        print("Resend error:", e)


def send_email_async(sender_email, sender_password, email, msg):
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print("Email failed:", e)

@app.route('/forgetPassword', methods=['POST'])
def forget_password():
    email = request.form['email']

    conn = get_db_connection()
    user = conn.execute(
        "SELECT id FROM Users_info WHERE Email_ID=?",
        (email,)
    ).fetchone()

    if not user:
        conn.close()
        flash("Email not found.", "danger")
        return redirect(url_for('form'))

    # Generate temporary password
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    hashed_password = generate_password_hash(temp_password)

    conn.execute(
        "UPDATE Users_info SET Password=? WHERE Email_ID=?",
        (hashed_password, email)
    )
    conn.commit()
    conn.close()

    # Send email in background thread
    thread = threading.Thread(
        target=send_email_resend,
        args=(email, temp_password)
    )
    thread.start()

    flash("Temporary password sent to your email.", "success")
    return redirect(url_for('form'))

# -------------------- LEADERBOARD --------------------
@app.route('/leaderboard')
def leaderboard():
    return render_template("leaderBoard.html", leaderboard=get_leaderboard())

def get_leaderboard():
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT Username, Portfolio_value, Balance
            FROM Users_info
            ORDER BY Balance DESC
            LIMIT 10
        """).fetchall()
        return rows
    finally:
        conn.close()

# -------------------- ACCOUNT --------------------
@app.route("/account")
def account():
    if "user_id" not in session:
        flash("Please log in to view your account.", "warning")
        return redirect(url_for('form'))

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT Username, id, Balance FROM Users_info WHERE id=?", (session["user_id"],))
        row = cur.fetchone()
        if not row:
            session.clear()
            flash("User not found. Please log in again.", "danger")
            return redirect(url_for('form'))

        username = row["Username"]
        user_id = row["id"]
        balance = row["Balance"]
        owned_shareData = getOwned_shareData(user_id)
        pnl_data = calculate_pnl_metrics(user_id, balance, owned_shareData)
    finally:
        conn.close()

    return render_template(
        "Account.html",
        username=username,
        user_id=user_id,
        owned_shares=owned_shareData,
        todays_pnl=pnl_data['todays_pnl'],
        total_investment=pnl_data['total_investment'],
        current_value=pnl_data['current_value']
    )

def getOwned_shareData(user_id):
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT symbol, quantity
            FROM Holdings
            WHERE user_id = ?
            ORDER BY quantity DESC
        """, (user_id,)).fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching owned shares: {e}")
        return []
    finally:
        conn.close()

def calculate_pnl_metrics(user_id, current_balance, owned_shares):
    try:
        from api.stocks_api import fetch_stock_price
        total_stock_value = 0
        for share in owned_shares:
            current_price = fetch_stock_price(share['symbol'])
            if current_price:
                total_stock_value += share['quantity'] * current_price
        current_portfolio_value = current_balance + total_stock_value
        initial_balance = 100000
        total_pnl = current_portfolio_value - initial_balance
        total_investment_in_stocks = initial_balance - current_balance
        return {
            'todays_pnl': round(total_pnl, 2),
            'total_investment': round(total_investment_in_stocks, 2),
            'current_value': round(current_portfolio_value, 2)
        }
    except Exception as e:
        print(f"Error calculating P&L metrics for user {user_id}: {e}")
        return {'todays_pnl': 0, 'total_investment': 0, 'current_value': current_balance}

# -------------------- DELETE ACCOUNT --------------------
@app.route("/delete-account", methods=["POST","GET"])
def delete_account():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please log in to perform this action."}), 401

    conn = get_db_connection()
    try:
        user_id = session["user_id"]
        conn.execute("DELETE FROM Holdings WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM Users_info WHERE id = ?", (user_id,))
        conn.commit()
        session.clear()
        return jsonify({"success": True, "message": "Your account has been deleted successfully."})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Error deleting account: {str(e)}"}), 500
    finally:
        conn.close()

# -------------------- Update Pass -------------------
@app.route("/update-password", methods=["POST"])
def update_password():
    if "user_id" not in session:
        flash("Please login first.", "danger")
        return redirect(url_for('form'))  # NOT 401

    newPass = request.form['update_pass1']
    confirmPass = request.form['update_pass2']

    # Validation
    if not newPass or not confirmPass:
        flash("Please fill all fields.", "danger")
        return redirect(url_for('account'))

    if newPass != confirmPass:
        flash("Passwords do not match.", "danger")
        return redirect(url_for('account'))

    if len(newPass) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for('account'))

    hashed_password = generate_password_hash(newPass)

    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE Users_info SET Password=? WHERE id=?",
            (hashed_password, session["user_id"])
        )
        conn.commit()
        flash("Password updated successfully!", "success")
    except Exception as e:
        conn.rollback()
        flash("Something went wrong!", "danger")
    finally:
        conn.close()

    return redirect(url_for('form'))
# -------------------- OTHER PAGES --------------------
@app.route("/help")
def help():
    return render_template("help.html")

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # True when using HTTPS

# -------------------- MAIN --------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
