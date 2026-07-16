import csv
from excel import COLUMNS

def store(rows, csv_file):
    does_file_exist = csv_file.exists()
    
    with open(csv_file, mode='a') as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        if not does_file_exist:
            writer.writeheader()
        writer.writerows(rows)
        
def load_existing_keys(csv_file):
    keys = set()
    if not csv_file.exists():
        return set()
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            keys.add((row['stock'], row['date'], row['name']))
    return keys

def load_all_rows(csv_file):
    if not csv_file.exists():
        return []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]
        