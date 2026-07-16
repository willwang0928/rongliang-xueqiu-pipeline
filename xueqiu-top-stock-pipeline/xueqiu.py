import json
from config import BASE_URL, MAX_PAGES, POSTS_PER_PAGE
import time

def fetch_hot_stocks(page):
    start = time.perf_counter()
    selector = 'div[class*="StockHotList_stock-hot__container"] a[href^="/S/"]'
    page.wait_for_selector(selector, timeout=30000)

    hrefs = page.eval_on_selector_all(
        selector,
        "els => els.map(el => el.getAttribute('href'))",
    )

    stocks = []
    for href in hrefs:
        code = href.split("/S/")[1]
        if code not in stocks:
            stocks.append(code)
    end = time.perf_counter()
    print(end-start)
    return stocks
def fetch_discussion_posts(page, stock: str, max_pages: int = MAX_PAGES, count: int = POSTS_PER_PAGE):
    all_posts = []

    try:
        page.goto(f'{BASE_URL}/S/{stock}', wait_until="domcontentloaded", timeout=20000)
    except Exception:
        pass

    page.wait_for_selector("text=讨论", timeout = 30000)
    for page_num in range(1, max_pages + 1):
        api_url = (
            "/query/v1/symbol/search/status.json"
            f"?count={count}&comment=0&symbol={stock}&hl=0&source=all"
            f"&sort=time&page={page_num}&q=&type=11"
        )
        
        result = page.evaluate(
            """
            async (url) => {
                const res = await fetch(url, { credentials: "include" });
                return { status: res.status, text: await res.text() };
            }
            """,
            api_url,
        )
    
        if result['status'] != 200:
            print(f"Page {page_num}: got status {result['status']}, stopping.")
            break
        
        data = json.loads(result['text'])
        items = data.get('list', [])
        if not items:
            break
        
        all_posts.extend(items)
        print(f'Page {page_num}: fetched {len(items)} posts.')
        page.wait_for_timeout(1000)
        
    return all_posts

