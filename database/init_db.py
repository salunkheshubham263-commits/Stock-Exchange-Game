import sqlite3

def init_db():
    #connect to database (creates users.db if it doesn't exist)
    conn = sqlite3.connect('stock_game.db')
    cursor = conn.cursor()
    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users_info
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
                First_Name Text not null,
                Last_Name text not null,
                Username text unique not null,
                Email_ID text unique not null,
                Password text not null
              )''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized with Users_info table.")
