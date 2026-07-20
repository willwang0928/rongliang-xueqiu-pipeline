import tushare as ts
import pandas as pd
import mplfinance as mpf
import storage.db as db


connection = db.get_connection()
cursor = connection.cursor()

cursor.execute(
    "SELECT stock FROM hot_stocks"
)

stocks = cursor.fetchall()

for i, stock in enumerate(stocks, start=1):
    print(f"{i}: {stock[0]}")

while True:
    choice = input(("Please enter a stock you want to visualize: "))
    try:
        choice = int(choice)
    except ValueError:
        pass
    
    if choice not in range(1, len(stocks) + 1):
        print("Please enter a valid integer")
    else:
        break
    
chosen_stock = stocks[choice - 1][0]
exchange = chosen_stock[0:2]
number = chosen_stock[2:]
corr_fmt = number + "." + exchange


if exchange not in ['SH', 'SZ'] or not number.isdigit():
    exit(f"{chosen_stock} isn't a Chinese A-share ticker - not supported yet")


# TODO: insert your Tushare token here before running
ts.set_token("YOUR_TUSHARE_TOKEN_HERE")
pro = ts.pro_api()

df = pro.daily(ts_code=corr_fmt, start_date='20260101', end_date='20260717')
if df.empty:
    df = pro.fund_daily(ts_code=corr_fmt, start_date='20260101', end_date='20260717')
if df.empty:
    exit(f"There currently has no price data for {chosen_stock}")

df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
df = df.set_index('trade_date')

df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'vol': 'Volume'})
df = df.sort_index(ascending=True)
df['MA5'] = df['Close'].rolling(5).mean()

apd = mpf.make_addplot(df['Close'], color='blue', width=2)
ma = mpf.make_addplot(df['MA5'], color='orange', width=2)

mpf.plot(df, type='candle', volume=False, addplot=[apd, ma])


