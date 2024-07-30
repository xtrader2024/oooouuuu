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

# USDT pariteleri
USDT_PAIRS = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "NEO/USDT", "LTC/USDT",
    "QTUM/USDT", "ADA/USDT", "XRP/USDT", "EOS/USDT", "TUSD/USDT",
    "IOTA/USDT", "XLM/USDT", "ONT/USDT", "TRX/USDT", "ETC/USDT",
    "ICX/USDT", "NULS/USDT", "VET/USDT", "USDC/USDT", "LINK/USDT",
    "ONG/USDT", "HOT/USDT", "ZIL/USDT", "ZRX/USDT", "FET/USDT",
    "BAT/USDT", "ZEC/USDT", "IOST/USDT", "CELR/USDT", "DASH/USDT",
    "MATIC/USDT", "ATOM/USDT", "TFUEL/USDT", "ONE/USDT", "FTM/USDT",
    "ALGO/USDT", "DOGE/USDT", "DUSK/USDT", "ANKR/USDT", "WIN/USDT",
    "COS/USDT", "MTL/USDT", "DENT/USDT", "KEY/USDT", "WAN/USDT",
    "FUN/USDT", "CVC/USDT", "CHZ/USDT", "BAND/USDT", "XTZ/USDT",
    "REN/USDT", "RVN/USDT", "HBAR/USDT", "NKN/USDT", "STX/USDT",
    "KAVA/USDT", "ARPA/USDT", "IOTX/USDT", "RLC/USDT", "CTXC/USDT",
    "BCH/USDT", "TROY/USDT", "VITE/USDT", "FTT/USDT", "EUR/USDT",
    "OGN/USDT", "WRX/USDT", "LSK/USDT", "BNT/USDT", "LTO/USDT",
    "MBL/USDT", "COTI/USDT", "STPT/USDT", "DATA/USDT", "SOL/USDT",
    "CTSI/USDT", "HIVE/USDT", "CHR/USDT", "ARDR/USDT", "MDT/USDT",
    "STMX/USDT", "KNC/USDT", "LRC/USDT", "COMP/USDT", "SC/USDT",
    "ZEN/USDT", "SNX/USDT", "VTHO/USDT", "DGB/USDT", "SXP/USDT",
    "MKR/USDT", "DCR/USDT", "STORJ/USDT", "MANA/USDT", "YFI/USDT",
    "BAL/USDT", "BLZ/USDT", "IRIS/USDT", "KMD/USDT", "JST/USDT",
    "SAND/USDT", "NMR/USDT", "DOT/USDT", "LUNA/USDT", "RSR/USDT",
    "PAXG/USDT", "TRB/USDT", "SUSHI/USDT", "KSM/USDT", "EGLD/USDT",
    "DIA/USDT", "RUNE/USDT", "FIO/USDT", "UMA/USDT", "BEL/USDT",
    "WING/USDT", "UNI/USDT", "OXT/USDT", "SUN/USDT", "AVAX/USDT",
    "FLM/USDT", "ORN/USDT", "UTK/USDT", "XVS/USDT", "ALPHA/USDT",
    "AAVE/USDT", "NEAR/USDT", "INJ/USDT", "AUDIO/USDT", "CTK/USDT",
    "AKRO/USDT", "AXS/USDT", "HARD/USDT", "STRAX/USDT", "UNFI/USDT",
    "ROSE/USDT", "AVA/USDT", "SKL/USDT", "SUSD/USDT", "XLMUP/USDT",
    "XLMDOWN/USDT"
]

# Göstergeler için sabitler
RSI_TIME_PERIOD = 14
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9
BOLLINGER_WINDOW = 20
STOCH_FASTK_PERIOD = 14
STOCH_SLOWK_PERIOD = 3

def fetch_data(symbol, interval='1d', lookback=365):
    exchange = ccxt.binance()
    since = exchange.parse8601((datetime.utcnow() - timedelta(days=lookback)).isoformat())
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=interval, since=since)
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    return df

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
    
    price = df['close'].iloc[-1]
    sma_50 = df['SMA_50'].iloc[-1]
    
    if pd.isna(sma_50) or sma_50 == 0:
        return np.nan, np.nan
    
    expected_price = price * (1 + (price - sma_50) / sma_50)
    expected_increase_percentage = ((expected_price - price) / price)
    
    return expected_price, expected_increase_percentage

# Streamlit arayüzü
st.title('Kripto Para Veri Analizi')

selected_pair = st.selectbox('Kripto Para Çifti Seçin', USDT_PAIRS)
data_interval = st.selectbox('Zaman Aralığı Seçin', ['1d', '1h', '30m', '15m'])
lookback_period = st.slider('Veri Gerçekleme Süresi (Gün)', min_value=30, max_value=365, value=90)

if st.button('Verileri Getir ve Analiz Et'):
    df = fetch_data(selected_pair, interval=data_interval, lookback=lookback_period)
    if df.empty:
        st.error('Veri alınamadı. Lütfen daha sonra tekrar deneyin.')
    else:
        df = calculate_indicators(df)
        df = generate_signals(df)
        forecast = forecast_next_price(df)
        expected_price, expected_increase_percentage = calculate_expected_price(df)
        
        st.write(f"Son Fiyat: {df['close'].iloc[-1]}")
        st.write(f"Beklenen Fiyat: {expected_price}")
        st.write(f"Beklenen Artış Yüzdesi: {expected_increase_percentage:.2%}")
        
        # Grafikler
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df.index, df['close'], label='Kapanış Fiyatı', color='blue')
        ax.plot(df.index, df['SMA_50'], label='SMA 50', color='red')
        ax.fill_between(df.index, df['BB_Lower'], df['BB_Upper'], color='grey', alpha=0.3, label='Bollinger Bands')
        ax.set_xlabel('Tarih')
        ax.set_ylabel('Fiyat')
        ax.set_title(f'{selected_pair} Fiyat Grafiği')
        ax.legend()
        
        st.pyplot(fig)
        
        # Beklenen fiyatı ve artışı gösteren grafik
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.plot(df.index, df['close'], label='Kapanış Fiyatı', color='blue')
        ax2.axhline(expected_price, color='green', linestyle='--', label='Beklenen Fiyat')
        ax2.set_xlabel('Tarih')
        ax2.set_ylabel('Fiyat')
        ax2.set_title(f'{selected_pair} Beklenen Fiyat Grafiği')
        ax2.legend()
        
        st.pyplot(fig2)
