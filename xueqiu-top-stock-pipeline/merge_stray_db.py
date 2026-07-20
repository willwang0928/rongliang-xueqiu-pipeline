import sqlite3
import storage.db as db

stray_connection = sqlite3.connect('/Users/williamwang/Desktop/Python/rongliang-xueqiu-pipeline/disc.db')
stray_cursor = stray_connection.cursor()

stray_cursor.execute("SELECT stock, date, name, content FROM disc_posts")
rows = stray_cursor.fetchall()

connection = db.get_connection()
cursor = connection.cursor()

for row in rows:
    cursor.execute(
            "INSERT OR IGNORE INTO disc_posts (stock, date, name, content) VALUES (?, ?, ?, ?)",
            (row[0], row[1], row[2], row[3])
        )
    
connection.commit()
