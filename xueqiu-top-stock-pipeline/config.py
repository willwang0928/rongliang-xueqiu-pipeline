from pathlib import Path

folder = Path(__file__).parent
OUTPUT_FILE = folder / "disc.xlsx"
CSV_FILE = folder / "disc.csv"
STOCK = []
BASE_URL = 'https://xueqiu.com'

MAX_PAGES = 3
POSTS_PER_PAGE = 20

RECHECK_INTERVAL_SECONDS = 300

DB_FILE = folder / "disc.db"

