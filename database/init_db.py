import sqlite3

def init_database():
    conn = sqlite3.connect('stock_game.db')
    cursor = conn.cursor()
    #create Users_info table with correct structure
    cursor.execute("""
                   Create table if not exists Users_info (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   First_Name text not null,
                   Last_Name text not null,
                   Username text not null unique,
                   Email_ID text not null unique,
                   Password text not null,
                   Balance integer default 100000,
                   Portfolio_value integer default 0,
                   Net_Worth integer default 0,
                   created_at datetime default current_timestamp
                   )
                   """)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()