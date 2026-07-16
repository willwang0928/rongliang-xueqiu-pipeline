import config, csv_store
from parser import parse_posts
from xueqiu import fetch_discussion_posts, fetch_hot_stocks

from playwright.sync_api import sync_playwright
import time

def main():
    while True:
        with sync_playwright() as p:
            start = time.perf_counter()
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            page = browser.new_page()
            
            try:
                page.goto(config.BASE_URL, wait_until='domcontentloaded', timeout=20000)
            except Exception:
                pass
            end = time.perf_counter()
            print(end-start)
            
            
            config.STOCK = fetch_hot_stocks(page)
            stocks = []
            for stock in config.STOCK:
                start = time.perf_counter()
                try:
                    raw = fetch_discussion_posts(page, stock)
                    rows = parse_posts(raw, stock)
                    stocks.extend(rows)
                except Exception as e:
                    print(f"Stock {stock} raised {e}")
                end = time.perf_counter()
                print(end-start)
            
            existing_keys = csv_store.load_existing_keys(config.CSV_FILE)
            new_rows = []
            for row in stocks:
                check = (row['stock'], row['date'], row['name'])
                if check not in existing_keys:
                    new_rows.append(row)
            
            csv_store.store(new_rows, config.CSV_FILE)
            print(f'Saved {len(new_rows)} posts to {config.CSV_FILE}')
        
            browser.close()
            
            time.sleep(config.RECHECK_INTERVAL_SECONDS)
    
if __name__ == "__main__":
    main()


