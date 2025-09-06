import requests
from flask import Blueprint, jsonify, request, session
import sqlite3, os

stocks_bp = Blueprint("stocks", __name__)

API_KEY = "d2ssee1r01qkuv3i7mrgd2ssee1r01qkuv3i7ms0"

def get_db_connection():
    conn = sqlite3.connect("stock_game.db")
    conn.row_factory = sqlite3.Row
    return conn

def fetch_stock_price(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get("c",0)

def list_stocks():
    symbols = ["AAPL", "MSFT","GOOG","AMZN","TSLA"]
    stocks = []
    for s in symbols:
        stocks.append({"symbol": s, "price": fetch_stock_price(s)})
        return jsonify(stocks)
    

def buy_stock():
    symbol = request.json["symbol"]
    qty = int(request.json["qty"])

    conn = get_db_connection()
    cur = conn.cursor()

    user_id = session["user_id"]
    user = cur.execute("SELECT Balance FROM Users_info WHERE id=?",(user_id,)).fetchone()
    balance = user["Balance"]

    price = fetch_stock_price(symbol)
    total_cost = price * qty

    if balance < total_cost:
        return jsonify({"status": "error", "message": "not enough balance"}),400
    
    cur.execute("Update user_info set Balance = Balance - ? WHERE id=?",(total_cost,user_id))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok","message":f"Bought {qty} shares of {symbol}"})

@stocks_bp.route("/sell", methods=["POST"])
def sell_stock():
    symbol = request.json["symbol"]
    qty = int(request.json["qty"])
    price = fetch_stock_price(symbol)
    total_income = price * qty

    conn = get_db_connection()
    cur = conn.cursor()
    user_id = session["user_id"]
    cur.execute("UPDATE Users_info SET Balance = Balance + ? WHERE id=?",(total_income,user_id))
    conn.commit()
    conn.close()

    return jsonify({"status":"ok","message":f"Sold{qty} shares of {symbol}"})




