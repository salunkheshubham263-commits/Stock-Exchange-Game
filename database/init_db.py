import os
from dotenv import load_dotenv
from sqlcipher3 import dbapi2 as sqlite3

load_dotenv()

def init_database():
    conn = sqlite3.connect('stock_game.db')
    conn.execute(f"PRAGMA key='{os.getenv('secret_key')}'")  # MUST set key immediately after connecting
    cursor = conn.cursor()
    
    # Create Users_info table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            First_Name TEXT NOT NULL,
            Last_Name TEXT NOT NULL,
            Username TEXT NOT NULL UNIQUE,
            Email_ID TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            Balance INTEGER DEFAULT 100000,
            Portfolio_value INTEGER DEFAULT 0,
            Net_Worth INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create Holdings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users_info(id)
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()
