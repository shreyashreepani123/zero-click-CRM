import sqlite3

def init_db():
    conn = sqlite3.connect("crm.db")
    conn.execute('''CREATE TABLE IF NOT EXISTS crm_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Company TEXT,
        Follow_up_Date TEXT,
        Notes TEXT
    )''')
    conn.commit()
    return conn

def insert_crm_entry(name, company, follow_up, notes):
    conn = sqlite3.connect("crm.db")
    conn.execute(
        "INSERT INTO crm_data (Name, Company, Follow_up_Date, Notes) VALUES (?, ?, ?, ?)",
        (name, company, follow_up, notes),
    )
    conn.commit()
    conn.close()

def get_all_entries():
    conn = sqlite3.connect("crm.db")
    rows = conn.execute("SELECT Name, Company, Follow_up_Date, Notes FROM crm_data").fetchall()
    conn.close()
    return rows
