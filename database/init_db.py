import sqlite3

#connect to database (creates users.db if it doesn't exist)
conn = sqlite3.connect('stock_game.db')
c = conn.cursor()
# Create users table
c.execute('''CREATE TABLE IF NOT EXISTS users
          (id INTEGER PRIMARY KEY AUTOINCREMENT,
          username Text UNIQUE ,password text
          )''')
conn.commit()
conn.close()
