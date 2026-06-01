import sqlite3
from datetime import datetime

DB_NAME = "prices.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            searched_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS price_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_id INTEGER,
            store TEXT,
            product_name TEXT,
            price INTEGER,
            price_display TEXT,
            link TEXT,
            image TEXT,
            recorded_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_search(query, results):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO searches (query, searched_at) VALUES (?, ?)",
        (query, now)
    )
    search_id = c.lastrowid
    for r in results:
        c.execute('''
            INSERT INTO price_results 
            (search_id, store, product_name, price, price_display, link, image, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            search_id,
            r["store"],
            r["name"],
            r["price"],
            r["price_display"],
            r["link"],
            r["image"],
            now
        ))
    conn.commit()
    conn.close()
    return search_id

def get_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM searches ORDER BY searched_at DESC LIMIT 10"
    )
    rows = c.fetchall()
    conn.close()
    return rows