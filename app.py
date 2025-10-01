from flask import Flask, request, redirect, url_for, flash, render_template, session, jsonify
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
        Balance
    FROM Users_info
    ORDER BY Balance DESC
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

@app.route("/account")
def account():
    # Check if user is logged in
    if "user_id" not in session:
        flash("Please log in to view your account.", "warning")
        return redirect(url_for('form'))
    
    conn = sqlite3.connect("stock_game.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # Get user info
        cur.execute("SELECT Username, id, Balance FROM Users_info WHERE id=?", (session["user_id"],))
        row = cur.fetchone()

        if row:
            username = row["Username"]
            user_id = row["id"]
            balance = row["Balance"]
            
            # Get user's owned shares
            owned_shareData = getOwned_shareData(user_id)
            
            # Calculate P&L metrics using current API data
            pnl_data = calculate_pnl_metrics(user_id, balance, owned_shareData)
            
        else:
            # User ID in session doesn't exist in database
            session.clear()
            flash("User not found. Please log in again.", "danger")
            return redirect(url_for('form'))

    except Exception as e:
        flash("Error accessing account information.", "danger")
        return redirect(url_for('home'))
    finally:
        conn.close()

    return render_template("Account.html", 
                         username=username, 
                         user_id=user_id, 
                         owned_shares=owned_shareData,
                         todays_pnl=pnl_data['todays_pnl'],
                         total_investment=pnl_data['total_investment'],
                         current_value=pnl_data['current_value'])

def getOwned_shareData(user_id):
    conn = get_db_connection()
    try:
        rows = conn.execute("""
        SELECT
            symbol,
            quantity
        FROM 
            Holdings
        WHERE 
            user_id = ?
        ORDER BY quantity DESC
        """, (user_id,)).fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching owned shares: {e}")
        return []
    finally:
        conn.close()

def calculate_pnl_metrics(user_id, current_balance, owned_shares):
    """
    Calculate P&L metrics for a specific user using current stock prices from API
    """
    try:
        # Import the fetch_stock_price function from your API
        from api.stocks_api import fetch_stock_price
        
        total_stock_value = 0
        stock_details = []
        
        # Calculate current value of all stocks for this user
        for share in owned_shares:
            symbol = share['symbol']
            quantity = share['quantity']
            
            # Get current price from API
            current_price = fetch_stock_price(symbol)
            
            if current_price:
                stock_value = quantity * current_price
                total_stock_value += stock_value
                stock_details.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'current_price': current_price,
                    'value': stock_value
                })
        
        # Calculate portfolio metrics for this specific user
        current_portfolio_value = current_balance + total_stock_value
        
        # Get the user's initial balance from database (default is 100,000)
        # Since all users start with 100,000, we can use that as initial balance
        initial_balance = 100000
        
        # Total P&L calculation for this user
        total_pnl = current_portfolio_value - initial_balance
        
        # Total cash invested in stocks for this user
        # This represents how much cash this user has spent on buying stocks
        total_investment_in_stocks = initial_balance - current_balance
        
        return {
            'todays_pnl': round(total_pnl, 2),
            'total_investment': round(total_investment_in_stocks, 2),
            'current_value': round(current_portfolio_value, 2)
        }
        
    except Exception as e:
        print(f"Error calculating P&L metrics for user {user_id}: {e}")
        # Return basic values if calculation fails
        return {
            'todays_pnl': 0,
            'total_investment': 0,
            'current_value': current_balance
        }


@app.route("/delete-account", methods=["POST","GET"])
def delete_account():
    # Check if user is logged in
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please log in to perform this action."}), 401
    
    conn = get_db_connection()
    try:
        user_id = session["user_id"]
        
        # Delete user's holdings first (due to foreign key constraint)
        conn.execute("DELETE FROM Holdings WHERE user_id = ?", (user_id,))
        
        # Delete user account
        conn.execute("DELETE FROM Users_info WHERE id = ?", (user_id,))
        
        conn.commit()
        
        # Clear the session
        session.clear()
        
        return jsonify({
            "success": True, 
            "message": "Your account has been deleted successfully."
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({
            "success": False, 
            "message": f"Error deleting account: {str(e)}"
        }), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    