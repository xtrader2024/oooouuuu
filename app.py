import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import requests
import statsmodels.api as sm
from datetime import datetime, timedelta

# CoinGecko API URL
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/"

# USDT pariteleri - CoinGecko'daki coin isimleri
USDT_PAIRS = [
    "bitcoin", "ethereum", "binancecoin", "neo", "litecoin",
    "qtum", "cardano", "ripple", "eos", "tusd",
    "iota", "stellar", "ontology", "tron", "ethereum-classic",
    "icon", "nuls", "vechain", "usd-coin", "link",
    "on-g", "hot", "zil", "zrx", "fet",
    "bat", "zec", "iost", "celer-network", "dash",
    "matic-network", "cosmos", "theta-fuel", "harmony", "fantom",
    "algorand", "dogecoin", "dusk-network", "ankr", "wink",
    "cosmos", "metal", "dent", "coti", "wanchain",
    "funfair", "civic", "chiliz", "band-protocol", "tezos",
    "ren", "ravencoin", "hedera", "nkn", "stx",
    "kava", "arpa-chain", "iotex", "rlc", "cyc",
    "bitcoin-cash", "troy", "vite", "ftx-token", "euro",
    "origin-protocol", "wazirx", "lisk", "bancor", "lto-network",
    "mbl", "coti", "stpt", "data", "solana",
    "covalent", "hive", "cherry-token", "ardor", "meditat",
    "stmx", "kyber-network", "loopring", "compound", "siacoin",
    "zen", "synths-network", "vechain-thor", "digibyte", "swipe",
    "maker", "decred", "storj", "decentraland", "yearn-finance",
    "balancer", "bluzelle", "iris-network", "komodo", "just",
    "sand", "numeraire", "polkadot", "terra-luna", "reserve-rights",
    "pax-gold", "thrive", "sushi", "kusama", "elrond",
    "dia", "thorchain", "firo", "uma", "bella-protocol",
    "wing-finance", "uniswap", "oxt", "sun", "avalanche",
    "fluence", "orion-protocol", "utrust", "venus", "alpha-finance",
    "aave", "near", "injective-protocol", "audius", "certik",
    "akropolis", "axie-infinity", "hard-protocol", "stratis", "unifi",
    "rose", "ava", "skale", "sushi", "xrp-up",
    "xlm-down"
]

# Göstergeler için sabitler
RSI_TIME_PERIOD = 14
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9
BOLLINGER_WINDOW = 20
STOCH_FASTK_PERIOD = 14
STOCH_SLOWK_PERIOD = 3

def fetch_data(symbol, interval='daily', lookback=365):
    symbol = symbol.split('/')[0].lower()  # CoinGecko için sadece ilk kısmı kullan
    granularity = 'daily' if interval == 'daily' else 'hourly'
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=lookback)
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    url = f"{COINGECKO_API_URL}coins/{symbol}/market_chart/range"
    params = {
        'vs_currency': 'usd',
        'from': start_timestamp,
        'to': end_timestamp
    }

    response = requests.get(url, params=params)
    data = response.json()
    
    prices = data['prices']
    
    df = pd.DataFrame(prices, columns=['timestamp', 'close'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    # Eksik verileri doldurmak için varsayılan değerler
    df['open'] = df['close']
    df['high'] = df['close']
    df['low'] = df['close']
    df['volume'] = np.nan
    
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
st.title('Cryptocurrency Data Analysis / Kripto Para Veri Analizi')

language = st.selectbox('Select Language / Dil Seçin', ['English', 'Turkish'])

selected_pair = st.selectbox('Select Cryptocurrency Pair / Kripto Para Çifti Seçin', USDT_PAIRS)
data_interval = st.selectbox('Select Time Interval / Zaman Aralığı Seçin', ['daily', 'hourly'])
lookback_period = st.slider('Lookback Period (Days) / Veri Gerçekleme Süresi (Gün)', min_value=30, max_value=365, value=90)

if st.button('Fetch and Analyze Data / Verileri Getir ve Analiz Et'):
    df = fetch_data(selected_pair, interval=data_interval, lookback=lookback_period)
    if df.empty:
        st.error('Data could not be retrieved. Please try again later. / Veri alınamadı. Lütfen daha sonra tekrar deneyin.')
    else:
        df = calculate_indicators(df)
        df = generate_signals(df)
        forecast = forecast_next_price(df)
        expected_price, expected_increase_percentage = calculate_expected_price(df)
        
        if language == 'English':
            st.write(f"Last Price: {df['close'].iloc[-1]}")
            st.write(f"Expected Price: {expected_price}")
            st.write(f"Expected Increase Percentage: {expected_increase_percentage:.2%}")
            st.write(f"Buy Signals: {df['Buy_Signal'].sum()} days")
            st.write(f"Sell Signals: {df['Sell_Signal'].sum()} days")
        else:
            st.write(f"Son Fiyat: {df['close'].iloc[-1]}")
            st.write(f"Beklenen Fiyat: {expected_price}")
            st.write(f"Beklenen Artış Yüzdesi: {expected_increase_percentage:.2%}")
            st.write(f"Alış Sinyalleri: {df['Buy_Signal'].sum()} gün")
            st.write(f"Satış Sinyalleri: {df['Sell_Signal'].sum()} gün")
        
        # Grafikler
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df.index, df['close'], label='Close Price / Kapanış Fiyatı', color='blue')
        ax.plot(df.index, df['SMA_50'], label='SMA 50', color='red')
        ax.fill_between(df.index, df['BB_Lower'], df['BB_Upper'], color='grey', alpha=0.3, label='Bollinger Bands')
        ax.set_xlabel('Date / Tarih')
        ax.set_ylabel('Price / Fiyat')
        ax.set_title(f'{selected_pair} Price Chart / {selected_pair} Fiyat Grafiği')
        ax.legend()
        
        st.pyplot(fig)
        
        # Beklenen fiyatı ve artışı gösteren grafik
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.plot(df.index, df['close'], label='Close Price / Kapanış Fiyatı', color='blue')
        ax2.axhline(expected_price, color='green', linestyle='--', label='Expected Price / Beklenen Fiyat')
        ax2.set_xlabel('Date / Tarih')
        ax2.set_ylabel('Price / Fiyat')
        ax2.set_title(f'{selected_pair} Expected Price Chart / {selected_pair} Beklenen Fiyat Grafiği')
        ax2.legend()
        
        st.pyplot(fig2)
