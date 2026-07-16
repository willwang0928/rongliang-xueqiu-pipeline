from openpyxl import Workbook
import time

COLUMNS = ['stock', 'name', 'date', 'content']

def save_posts(rows, output_file):
    start = time.perf_counter()
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(COLUMNS)
    
    for row in rows:
        sheet.append([row.get(column, '') for column in COLUMNS])
        
    workbook.save(output_file)
    end = time.perf_counter()
    print(end-start)
    return output_file
