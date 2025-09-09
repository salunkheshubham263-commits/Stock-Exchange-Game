import requests 
from flask import Blueprint, jsonify, request, session 
import time
price_cache = {}
last_fetch_time = {}
import sqlite3, os 
from dotenv import load_dotenv 
stocks_bp = Blueprint("stocks", __name__) 
load_dotenv() 
API_KEY = os.getenv("Api_Key") 
def get_db_connection(): 
    conn = sqlite3.connect("stock_game.db") 
    conn.row_factory = sqlite3.Row 
    return conn 


def fetch_stock_price(symbols): 
    now = time.time()
    if symbols in price_cache and now - last_fetch_time[symbols] < 5:
        return price_cache[symbols]
    
    url = f"https://finnhub.io/api/v1/quote?symbol={symbols}&token={API_KEY}" 
    response = requests.get(url) 
    data = response.json()

    price_cache[symbols] = data.get("c",0)
    last_fetch_time[symbols] = now 
    return data.get("c",0) 
@stocks_bp.route("/list", methods=["GET"]) 
def list_stocks(): 
    symbols = ["AAPL", "MSFT","GOOG","AMZN","NVDA",] 
    stocks = [] 
    for s in symbols: 
        stocks.append({"symbol": s, "price": fetch_stock_price(s)}) 
    return jsonify(stocks)

@stocks_bp.route("/buy", methods=["POST"]) 
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
    cur.execute("UPDATE Users_info SET Balance = Balance - ? WHERE id=?",(total_cost,user_id)) 
    
    holding = cur.execute("SELECT quantity FROM Holdings WHERE user_id=? AND symbol=?",(user_id,symbol)).fetchone()
    if holding:
        cur.execute("UPDATE Holdings SET quantity = quantity + ? WHERE user_id=? AND symbol=?",(qty,user_id,symbol))
    else:
        cur.execute("INSERT INTO Holdings (user_id, symbol, quantity) VALUES (?,?,?)", (user_id, symbol, qty))   
   
    conn.commit()

    new_balance = cur.execute("SELECT Balance FROM Users_info WHERE id=?", (user_id,)).fetchone()["Balance"]
    conn.close()

    return jsonify({"status": "ok","message":f"Bought {qty} shares of {symbol}", "new_balance": round(new_balance, 2)}) 

@stocks_bp.route("/sell", methods=["POST"]) 
def sell_stock(): 
    symbol = request.json["symbol"]
    qty = int(request.json["qty"])
    conn = get_db_connection()
    cur = conn.cursor()

    user_id = session["user_id"]
    holding = cur.execute("SELECT quantity FROM Holdings WHERE user_id=? AND symbol=?",(user_id, symbol)).fetchone()
    
    if not holding or holding["quantity"] < qty:
        return jsonify({"status": "error", "message": "not enough shares to sell"}),400
    
    price = fetch_stock_price(symbol)
    total_income = price * qty

    if holding["quantity"] == qty:
        cur.execute("DELETE FROM Holdings WHERE user_id =? AND symbol=?",(user_id,symbol))
    else:
        cur.execute("UPDATE Holdings SET quantity = quantity - ? WHERE user_id=? AND symbol=?",(qty, user_id, symbol))

    cur.execute("UPDATE Users_info SET Balance = Balance + ? WHERE id=?",(total_income, user_id))

    conn.commit()

    new_balance = cur.execute("SELECT Balance FROM Users_info WHERE id=?", (user_id,)).fetchone()["Balance"]
    conn.close()

    return jsonify({"status": "ok","message":f"sold {qty} shares of {symbol}","new_balance": round(new_balance, 2)})
    