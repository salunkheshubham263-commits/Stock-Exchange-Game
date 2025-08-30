import sqlite3

# Connect to the SQLite database (change 'your_database.db' to your actual database file)
conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Leaderboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    portfolio_value INTEGER DEFAULT 0,
    balance INTEGER DEFAULT 0,
    net_worth INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users_info(id)
)
""")

conn.commit()
conn.close()