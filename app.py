from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"   # needed for sessions and flash messages

# Function to connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect("stock_game.db")   # database file in your project
    conn.row_factory = sqlite3.Row            # lets us use dict-like access
    return conn


# ------------------- ROUTES -------------------

# Login Page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("home_page.html")


# Home Page
@app.route("/home")
def home():
    if "user" in session:
        return f"Welcome, {session['user']}!"
    else:
        return redirect(url_for("login"))


# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ------------------- MAIN -------------------
if __name__ == "__main__":
    app.run(debug=True)