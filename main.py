import ccxt
import pandas as pd
import time
import os
from ta.volatility import DonchianChannel
from ta.volume import ChaikinMoneyFlowIndicator

api_key = os.getenv("API_KEY")
secret = os.getenv("SECRET_KEY")

exchange = ccxt.mexc({
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True
})

symbol = 'MOODENG/USDT'
timeframe = '15m'
limit = 100

def fetch_ohlcv():
    data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def apply_indicators(df):
    dc = DonchianChannel(high=df['high'], low=df['low'], close=df['close'], window=20)
    cmf = ChaikinMoneyFlowIndicator(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=20)

    df['donchian_upper'] = dc.donchian_channel_hband()
    df['donchian_lower'] = dc.donchian_channel_lband()
    df['cmf'] = cmf.chaikin_money_flow()

    return df

def strategy(df):
    last = df.iloc[-1]
    previous = df.iloc[-2]

    if last['close'] > last['donchian_upper'] and last['cmf'] > 0:
        print(f"[{last['timestamp']}] ✅ BUY Signal - Price: {last['close']} coin: {[symbol]}")
    elif last['close'] < last['donchian_lower'] and last['cmf'] < 0:
        print(f"[{last['timestamp']}] ❌ SELL Signal - Price: {last['close']} coin: {[symbol]}")
    else:
        print(f"[{last['timestamp']}] ⏳ HOLD - Price: {last['close']} coin: {[symbol]}")

while True:
    df = fetch_ohlcv()
    df = apply_indicators(df)
    strategy(df)
    time.sleep(60 * 15) 
