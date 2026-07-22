# Xueqiu Hot-Stock Discussion Pipeline

A Python pipeline that scrapes the currently trending stocks and their discussion threads from [Xueqiu](https://xueqiu.com) (雪球) — a Chinese social investing platform — stores everything in SQLite, and provides an interactive tool to chart price history for any of the currently hot stocks.

## What it does

1. **Scrapes** Xueqiu's homepage for the current list of hottest stocks (filtered to Chinese A-share tickers only).
2. **Scrapes** the discussion/comment feed for each of those stocks.
3. **Stores** posts in a local SQLite database, deduplicated so repeated runs never create duplicate rows.
4. **Tracks** the current hot-stock list separately from historical post data, so downstream tools always reflect "what's hot right now," not an accumulation of every stock ever seen.
5. **Visualizes** price history as a candlestick chart (with a 5-day moving average) for any currently hot stock, using live market data from Tushare.
6. **Exports** the full discussion history to Excel on demand.

## Why it's built this way

Xueqiu's homepage widget updates continuously, and this pipeline is designed to run indefinitely, re-scraping every 5 minutes. Two things fell out of that:

- **Current state needs its own table.** Naively keeping only the historical `disc_posts` table meant that "which stocks are hot" was really "every stock that has ever been hot since the pipeline started," which grows unbounded and quickly becomes stale/noisy. A separate `hot_stocks` table is fully overwritten every scrape cycle, so it always reflects only the most recent snapshot — a small example of the "current snapshot vs. event log" pattern used in larger data systems.
- **Xueqiu's "hot stocks" widget isn't China-only.** It also surfaces global tickers (e.g. `AAPL`), so the scraper filters to `SH`/`SZ`-prefixed tickers (the Shanghai/Shenzhen exchange prefixes for Chinese A-shares) at the source, with a second independent validation check in the charting tool as a safety net.
- **Not every valid ticker has price data under the same API endpoint.** Some Chinese tickers are ETFs/funds rather than plain equities and only appear under Tushare's `fund_daily()` endpoint, not `daily()`. The charting tool tries both and exits gracefully if neither has data, instead of crashing.

## Architecture

```
main.py (runs forever, one scrape cycle every 5 minutes)
  └─ scraping/xueqiu.py       Playwright browser automation: hot-stock list + per-stock discussion posts
  └─ scraping/parser.py       Cleans HTML, formats timestamps, flattens raw JSON into rows
  └─ storage/db.py            SQLite: permanent post history + current hot-stock snapshot

price_chart.py (run on demand)
  └─ Reads current hot stocks from SQLite → fetches price data from Tushare → renders candlestick chart

export.py (run on demand)
  └─ Reads full post history from SQLite → writes disc.xlsx
```

## Database schema

```sql
CREATE TABLE disc_posts (
    stock   TEXT,
    date    TEXT,
    name    TEXT,
    content TEXT,
    UNIQUE(stock, date, name)
);

CREATE TABLE hot_stocks (
    stock TEXT PRIMARY KEY
);
```

- `disc_posts` — permanent, append-only history of every discussion post ever scraped. Deduplicated via a `UNIQUE` constraint + `INSERT OR IGNORE`, so re-running the scraper is always safe.
- `hot_stocks` — cleared and rebuilt every scrape cycle. Reflects only the most recent run's hot-stock list.

## Tech stack

| Purpose | Library |
|---|---|
| Browser automation / scraping | [Playwright](https://playwright.dev/python/) |
| HTML cleaning | BeautifulSoup4 |
| Data storage | SQLite (stdlib) |
| Market price data | [Tushare](https://tushare.pro/) |
| Data wrangling | pandas |
| Candlestick charts | mplfinance |
| Excel export | openpyxl |

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

You'll also need a free [Tushare](https://tushare.pro/) API token to fetch price data. Open `price_chart.py` and replace the placeholder:

```python
ts.set_token("YOUR_TUSHARE_TOKEN_HERE")
```

## Usage

Run the scraper first — it loops forever, so let it complete at least one cycle (watch for a `Saved X new posts` line) before moving on:

```bash
python main.py
```

Then, in a separate run, chart any of the currently hot stocks:

```bash
python price_chart.py
```

You'll see a numbered menu of the current hot stocks; pick one to render its candlestick chart.

To export the full discussion history to Excel:

```bash
python export.py
```

## Project structure

```
main.py                  Pipeline orchestrator / entrypoint
price_chart.py            Interactive candlestick chart tool
export.py                 Excel export tool
config.py                 Paths, URLs, and tunable constants
scraping/
  xueqiu.py                Playwright scraping logic
  parser.py                Post cleaning / normalization
storage/
  db.py                     SQLite schema + read/write helpers
  excel.py                  Excel writer
  csv_store.py              Legacy CSV backend (used by migrate.py)
migrate.py                 One-time CSV → SQLite migration
merge_stray_db.py          One-time recovery script for a path-bug-created stray database
requirements.txt
```

## Notes

- The scraper is intentionally resilient to partial failures: if scraping one stock's discussion feed throws an exception, the error is logged and the loop moves on to the next stock rather than crashing the whole run.
- All file paths are resolved relative to the project directory (not the current working directory), so scripts behave the same regardless of where they're launched from.
