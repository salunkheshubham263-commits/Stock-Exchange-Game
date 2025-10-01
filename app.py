from flask import Flask, request, redirect, url_for, flash, render_template, session, jsonify
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
app.secret_key = os.urandom(24)

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

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO Users_info (First_Name, Last_Name, Username, Email_ID, Password) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, username, email, password)
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
            "SELECT * FROM Users_info WHERE Email_ID=? AND Password=?",
            (email, password)
        ).fetchone()
    finally:
        conn.close()

    if user:
        session['user_id'] = user['id']
        session['user'] = user['Username']
        flash("Login successful!", "success")
        return redirect(url_for('home'))
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('form'))

# -------------------- FORGOT PASSWORD --------------------
@app.route('/forgetPassword', methods=['POST'])
def forget_password():
    email = request.form['email']
    conn = get_db_connection()
    try:
        user = conn.execute("SELECT Password FROM Users_info WHERE Email_ID=?", (email,)).fetchone()
    finally:
        conn.close()

    if user:
        password = user["Password"]
        sender_email = os.getenv("EMAIL_USER")
        sender_password = os.getenv("EMAIL_PASS")
        receiver_email = email

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "Your Password for Stock Exchange Game"
        msg.attach(MIMEText(f"Your password is: {password}", 'plain'))

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

# -------------------- OTHER PAGES --------------------
@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/privacy")
def privacy():
    return render_template("privacyPolicy.html")

# -------------------- MAIN --------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
