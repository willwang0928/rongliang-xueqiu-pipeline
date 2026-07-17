import config
from storage import db, excel

connection = db.get_connection()
cursor = connection.cursor()
cursor.execute("SELECT stock, name, date, content FROM disc_posts ORDER BY stock ASC, date DESC")

raw_rows = cursor.fetchall()

rows = [dict(zip(excel.COLUMNS, row)) for row in raw_rows]
excel.save_posts(rows, config.OUTPUT_FILE)