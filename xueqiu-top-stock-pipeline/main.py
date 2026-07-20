import config
from storage import db
from scraping.parser import parse_posts
from scraping.xueqiu import fetch_discussion_posts, fetch_hot_stocks

from playwright.sync_api import sync_playwright
import time

def main():
    connection = db.get_connection()
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
            hot_stocks = db.set_hot_stocks(config.STOCK, connection)
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
            
            start = time.perf_counter()
            saved_count = db.store(stocks, connection)
            end = time.perf_counter()
            print(end-start)
            print(f'Saved {saved_count} new posts')
        
            browser.close()
            
            time.sleep(config.RECHECK_INTERVAL_SECONDS)
    
if __name__ == "__main__":
    main()


