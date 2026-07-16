import config, csv_store, excel

rows = csv_store.load_all_rows(config.CSV_FILE)

rows.sort(key=lambda row: row['date'], reverse=True) 
rows.sort(key=lambda row: row['stock'])

excel.save_posts(rows, config.OUTPUT_FILE)