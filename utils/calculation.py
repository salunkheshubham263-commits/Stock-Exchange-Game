import random
import sqlite3
#stock prices
stocks = ["INFOSYS","TATA","ADANI","MICROSOFT","NIFTY","AMAZON"]

def get_stock_prices():
    prices = {name: random.randint(100,1000) for name in stocks}
    return prices
