import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
import statsmodels.api as sm
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
from decimal import Decimal, getcontext
import time

# Daha yüksek hassasiyet ayarlama
getcontext().prec = 50

# En çok bilinen 5 borsa kodları
TOP_EXCHANGES = {
    'Binance us': 'binanceus',
    'Kraken': 'kraken',
    'Bitfinex': 'bitfinex',
    'Bitstamp': 'bitstamp'
}

# Göstergeler için sabitler
BOLLINGER_WINDOW = 20
RSI_TIME_PERIOD = 14
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9
STOCH_FASTK_PERIOD = 14
STOCH_SLOWK_PERIOD = 3

def initialize_exchange(exchange_code):
    try:
        exchange = getattr(ccxt, exchange_code)()
        return exchange
    except Exception as e:
        st.error(f"Borsa başlatma hatası ({exchange_code}): {e}")
        return None

def get_exchange_data(symbol, interval, start_str, end_str, exchange):
    try:
        since = exchange.parse8601(start_str)
        df_list = []
        while since < exchange.parse8601(end_str):
            klines = exchange.fetch_ohlcv(symbol, interval, since=since, limit=1000)
            if not klines:
                break
            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']]
            df = df.astype(float)
            df_list.append(df)
            since = df.index[-1] + pd.Timedelta(seconds=1)  # Bir sonraki veri dilimi
            time.sleep(1)  # Gecikme ekle

        if not df_list:
            st.warning(f"Yetersiz veri ({symbol})")
            return pd.DataFrame()

        df = pd.concat(df_list)
        
        # Bitiş tarihini veri setinin son tarihi ile güncelle
        if end_str:
            df = df.loc[start_str:end_str]
        
        return df
    except Exception as e:
        st.error(f"Veri çekme hatası ({symbol}): {e}")
        time.sleep(60)  # 1 dakika bekle
        return pd.DataFrame()

def fetch_current_price(symbol, exchange):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last'], ticker['timestamp']  # Anlık fiyat ve timestamp getirir
    except Exception as e:
        st.error(f"Anlık fiyat çekme hatası ({symbol}): {e}")
        return None, None

def calculate_indicators(df):
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
    
    df['BB_Middle'] = df['close'].rolling(window=BOLLINGER_WINDOW).mean()
    df['BB_Upper'] = df['BB_Middle'] + 2 * df['close'].rolling(window=BOLLINGER_WINDOW).std()
    df['BB_Lower'] = df['BB_Middle'] - 2 * df['close'].rolling(window=BOLLINGER_WINDOW).std()
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=RSI_TIME_PERIOD).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_TIME_PERIOD).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['MACD_Line'] = df['close'].ewm(span=MACD_FAST_PERIOD, adjust=False).mean() - df['close'].ewm(span=MACD_SLOW_PERIOD, adjust=False).mean()
    df['MACD_Signal'] = df['MACD_Line'].ewm(span=MACD_SIGNAL_PERIOD, adjust=False).mean()
    
    df['Prev_Close'] = df['close'].shift(1)
    df['TR'] = df[['high', 'Prev_Close']].max(axis=1) - df[['low', 'Prev_Close']].min(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()

    df['Lowest_Low'] = df['low'].rolling(window=STOCH_FASTK_PERIOD).min()
    df['Highest_High'] = df['high'].rolling(window=STOCH_FASTK_PERIOD).max()
    df['%K'] = 100 * (df['close'] - df['Lowest_Low']) / (df['Highest_High'] - df['Lowest_Low'])
    df['%D'] = df['%K'].rolling(window=STOCH_SLOWK_PERIOD).mean()
    
    return df

def generate_signals(df):
    df['Buy_Signal'] = (df['close'] > df['SMA_50']) & (df['MACD_Line'] > df['MACD_Signal']) & (df['%K'] > df['%D']) & (df['%K'] > 20)
    df['Sell_Signal'] = (df['close'] < df['SMA_50']) & (df['RSI'] > 70)
    return df

def forecast_next_price(df):
    df = df.copy()
    df['day'] = np.arange(len(df))
    X = df[['day']]
    y = df['close']
    
    model = sm.OLS(y, sm.add_constant(X)).fit()
    
    next_day_index = np.array([[len(df) + 1]])
    next_day_df = pd.DataFrame(next_day_index, columns=['day'])
    next_day_df = sm.add_constant(next_day_df, has_constant='add')
    
    forecast = model.predict(next_day_df)
    
    return forecast[0]

def calculate_expected_price(df):
    if df.empty:
        return np.nan, np.nan
    
    price = Decimal(df['close'].iloc[-1])
    sma_50 = Decimal(df['SMA_50'].iloc[-1])
    
    if pd.isna(sma_50) or sma_50 == 0:
        return np.nan, np.nan
    
    expected_price = price * (1 + (price - sma_50) / sma_50)
    expected_increase_percentage = ((expected_price - price) / price) * 100 - 1
    
    return float(expected_price), float(expected_increase_percentage)

def calculate_trade_levels(df, entry_pct=0.02, take_profit_pct=0.05, stop_loss_pct=0.02):
    if df.empty:
        return np.nan, np.nan, np.nan
    
    entry_price = Decimal(df['close'].iloc[-1])
    take_profit_price = entry_price * (1 + Decimal(take_profit_pct))
    stop_loss_price = entry_price * (1 - Decimal(stop_loss_pct))
    
    return float(entry_price), float(take_profit_price), float(stop_loss_price)

def get_all_usdt_pairs(exchange):
    try:
        exchange_info = exchange.load_markets()
        symbols = exchange_info.keys()
        usdt_pairs = [s for s in symbols if s.endswith('/USDT')]
        return usdt_pairs
    except Exception as e:
        st.error(f"USDT paritesi çekme hatası: {e}")
        return []

def plot_to_png(df, symbol):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df.index, df['close'], label='Kapanış Fiyatı', color='blue')
    ax.plot(df.index, df['SMA_50'], label='50 Günlük SMA', color='green')
    ax.plot(df.index, df['EMA_50'], label='50 Günlük EMA', color='red')
    ax.plot(df.index, df['BB_Upper'], label='BB Üst Bandı', color='purple', linestyle='--')
    ax.plot(df.index, df['BB_Lower'], label='BB Alt Bandı', color='purple', linestyle='--')
    ax.plot(df.index, df['ATR'], label='ATR', color='orange')
    ax.set_title(f'{symbol} Analizi')
    ax.set_xlabel('Tarih')
    ax.set_ylabel('Fiyat')
    ax.legend()

    # Bilimsel notasyonun uygulanmasını sağla
    ax.ticklabel_format(axis='y', style='scientific', scilimits=(0,0))

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return img_base64

def main():
    st.title('Kripto Para Analiz Aracı')

    exchange_code = st.selectbox("Borsa Seçin", list(TOP_EXCHANGES.keys()))
    exchange = initialize_exchange(TOP_EXCHANGES[exchange_code])
    
    if exchange is None:
        st.stop()

    symbol = st.text_input("USDT Paritesi (örnek: BTC/USDT)", "BTC/USDT")
    interval = st.selectbox("Zaman Aralığı", ['1m', '5m', '15m', '30m', '1h', '4h', '1d'])
    start_date = st.date_input("Başlangıç Tarihi", datetime.today() - timedelta(days=30))
    end_date = st.date_input("Bitiş Tarihi", datetime.today())
    
    if st.button("Veriyi Çek"):
        start_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        df = get_exchange_data(symbol, interval, start_str, end_str, exchange)
        
        if not df.empty:
            df = calculate_indicators(df)
            df = generate_signals(df)
            expected_price, expected_increase_pct = calculate_expected_price(df)
            entry_price, take_profit_price, stop_loss_price = calculate_trade_levels(df)
            
            st.write(f"Son Kapanış Fiyatı: {df['close'].iloc[-1]}")
            st.write(f"Beklenen Fiyat: {expected_price}")
            st.write(f"Beklenen Artış Yüzdesi: {expected_increase_pct:.2f}%")
            st.write(f"Alım Fiyatı: {entry_price}")
            st.write(f"Kar Al Fiyatı: {take_profit_price}")
            st.write(f"Zarar Durdur Fiyatı: {stop_loss_price}")

            img_base64 = plot_to_png(df, symbol)
            st.image(f"data:image/png;base64,{img_base64}", use_column_width=True)
            
            st.write("Alım Satım Sinyalleri:")
            st.write(df[['close', 'Buy_Signal', 'Sell_Signal']].tail())

if __name__ == "__main__":
    main()
