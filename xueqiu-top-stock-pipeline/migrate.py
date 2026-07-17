from storage.csv_store import load_all_rows
from storage.db import get_connection
import config

rows = load_all_rows(config.CSV_FILE)
connection = get_connection()
cursor = connection.cursor()

for row in rows:
    cursor.execute(
        "INSERT OR IGNORE INTO disc_posts (stock, date, name, content) VALUES (?, ?, ?, ?)",
        (row['stock'], row['date'], row['name'], row['content'])
    )
connection.commit()
