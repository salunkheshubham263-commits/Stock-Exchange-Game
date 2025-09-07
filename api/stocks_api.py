import requests, sqlite3, os
from flask import Blueprint, jsonify, request, session
from dotenv import load_dotenv

stocks_bp = Blueprint("stocks", __name__)
load_dotenv()
API_KEY = os.getenv("Api_Key")
DB = "stock_game.db"

def get_db_connection():
    conn = sqlite3.connect("DB")
    conn.row_factory = sqlite3.Row
    return conn

def fetch_stock_price(symbols):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbols}&token={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get("c",0)

@stocks_bp.route("/list", methods=["GET"])
def list_stocks():
    symbols = ["AAPL", "MSFT","GOOG","AMZN","TSLA"]
    stocks = []
    for s in symbols:
        stocks.append({"symbol": s, "price": fetch_stock_price(s)})
    return jsonify(stocks)

@stocks_bp.route("/buy", methods=["POST"])
def buy_stock():
    if "user_id" not in session:
        return jsonify({"status":"error", "message":"Not Logged In"}),401
    symbol = request.json["symbol"]
    qty = int(request.json["qty", 0])
    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()
    user = cur.execute("SELECT Balace, Portfolio FROM Users_info WHERE id=?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({"status":"error","message":"User not found Please Sign Up."}),404
    balance = user["Balance"]
    price = fetch_stock_price(symbol)
    total_cost = price * qty

    if balance < total_cost:
        return jsonify({"status": "error", "message": "not enough balance"}),400
    
    # Deduct balance and increase total shares (portfolio)
    cur.execute("UPDATE Users_info SET Balance = Balance - ? WHERE id=?",(total_cost,user_id))
    conn.commit()

    new_data = cur.execute("SELECT Balance, Portfolio FROM Users_info WHERE id=?", (user_id,)).fetchone()
    conn.close()

    return jsonify({"status": "ok","message":f"Bought {qty} shares of {symbol}","new_balance": new_data['Balance'],"total_shares": new_data['Portfolio']})

@stocks_bp.route("/sell", methods=["POST"])
def sell_stock():
    if "user_id" not in session:
        return jsonify({"status":"error","message":"Not Logged In"}),401
    symbol = request.json.get("symbol")
    qty = int(request.json.get("qty",0))
    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()
    user = cur