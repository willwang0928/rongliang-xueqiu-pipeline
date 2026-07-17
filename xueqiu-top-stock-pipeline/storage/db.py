import sqlite3

def get_connection():
    with sqlite3.connect('disc.db') as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS disc_posts(
                "stock" TEXT,
                "date" TEXT,
                "name" TEXT,
                "content" TEXT,
                UNIQUE("stock", "date", "name")
            )
            """
        
        )
        return connection
    
def store(rows, connection):
    cursor = connection.cursor()
    running_total = 0
    for row in rows:
        cursor.execute(
            "INSERT OR IGNORE INTO disc_posts (stock, date, name, content) VALUES (?, ?, ?, ?)",
            (row["stock"], row["date"], row["name"], row["content"])
        )
        running_total += cursor.rowcount
    connection.commit()
    return running_total