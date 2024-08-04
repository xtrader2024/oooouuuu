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

# Language dictionaries
translations = {
    'English': {
        'title': 'Cryptocurrency Data Analysis',
        'select_pair': 'Select Cryptocurrency Pair',
        'select_interval': 'Select Time Interval',
        'lookback_period': 'Lookback Period (Days)',
        'fetch_button': 'Fetch and Analyze Data',
        'data_error': 'Data could not be retrieved. Please try again later.',
        'last_price': 'Last Price',
        'expected_price': 'Expected Price',
        'expected_increase_percentage': 'Expected Increase Percentage',
        'buy_signals': 'Buy Signals',
        'sell_signals': 'Sell Signals',
        'indicators': 'Indicators',
        'sma_50': 'SMA 50',
        'ema_50': 'EMA 50',
        'rsi': 'RSI',
        'macd_line': 'MACD Line',
        'macd_signal': 'MACD Signal',
        'atr': 'ATR',
        'percent_k': '%K',
        'percent_d': '%D',
        'bollinger_upper': 'Bollinger Bands (Upper)',
        'bollinger_lower': 'Bollinger Bands (Lower)',
        'chart_title': 'Price Chart',
        'expected_price_chart_title': 'Expected Price Chart'
    },
    'Turkish': {
        'title': 'Kripto Para Veri Analizi',
        'select_pair': 'Kripto Para Çifti Seçin',
        'select_interval': 'Zaman Aralığı Seçin',
        'lookback_period': 'Veri Gerçekleme Süresi (Gün)',
        'fetch_button': 'Verileri Getir ve Analiz Et',
        'data_error': 'Veri alınamadı. Lütfen daha sonra tekrar deneyin.',
        'last_price': 'Son Fiyat',
        'expected_price': 'Beklenen Fiyat',
        'expected_increase_percentage': 'Beklenen Artış Yüzdesi',
        'buy_signals': 'Alış Sinyalleri',
        'sell_signals': 'Satış Sinyalleri',
        'indicators': 'Göstergeler',
        'sma_50': 'SMA 50',
        'ema_50': 'EMA 50',
        'rsi': 'RSI',
        'macd_line': 'MACD Çizgisi',
        'macd_signal': 'MACD Sinyal',
        'atr': 'ATR',
        'percent_k': '%K',
        'percent_d': '%D',
        'bollinger_upper': 'Bollinger Bands (Üst)',
        'bollinger_lower': 'Bollinger Bands (Alt)',
        'chart_title': 'Fiyat Grafiği',
        'expected_price_chart_title': 'Beklenen Fiyat Grafiği'
    },
    'Chinese': {
        'title': '加密货币数据分析',
        'select_pair': '选择加密货币对',
        'select_interval': '选择时间间隔',
        'lookback_period': '回溯周期（天）',
        'fetch_button': '获取并分析数据',
        'data_error': '无法获取数据。请稍后再试。',
        'last_price': '最新价格',
        'expected_price': '预期价格',
        'expected_increase_percentage': '预期增长百分比',
        'buy_signals': '买入信号',
        'sell_signals': '卖出信号',
        'indicators': '指标',
        'sma_50': 'SMA 50',
        'ema_50': 'EMA 50',
        'rsi': 'RSI',
        'macd_line': 'MACD 线',
        'macd_signal': 'MACD 信号',
        'atr': 'ATR',
        'percent_k': '%K',
        'percent_d': '%D',
        'bollinger_upper': '布林带（上）',
        'bollinger_lower': '布林带（下）',
        'chart_title': '价格图表',
        'expected_price_chart_title': '预期价格图表'
    },
    'Hindi': {
        'title': 'क्रिप्टोकरेंसी डेटा विश्लेषण',
        'select_pair': 'क्रिप्टोकरेंसी पेयर चुनें',
        'select_interval': 'समय अंतराल चुनें',
        'lookback_period': 'लुकबैक अवधि (दिन)',
        'fetch_button': 'डेटा लाएं और विश्लेषण करें',
        'data_error': 'डेटा प्राप्त नहीं हो सका। कृपया बाद में पुनः प्रयास करें।',
        'last_price': 'अंतिम मूल्य',
        'expected_price': 'अपेक्षित मूल्य',
        'expected_increase_percentage': 'अपेक्षित वृद्धि प्रतिशत',
        'buy_signals': 'खरीद संकेत',
        'sell_signals': 'बेचने के संकेत',
        'indicators': 'संकेतक',
        'sma_50': 'SMA 50',
        'ema_50': 'EMA 50',
        'rsi': 'RSI',
        'macd_line': 'MACD लाइन',
        'macd_signal': 'MACD सिग्नल',
        'atr': 'ATR',
        'percent_k': '%K',
        'percent_d': '%D',
        'bollinger_upper': 'बोलिंजर बैंड (ऊपरी)',
        'bollinger_lower': 'बोलिंजर बैंड (निचला)',
        'chart_title': 'मूल्य चार्ट',
        'expected_price_chart_title': 'अपेक्षित मूल्य चार्ट'
    },
    'Arabic': {
        'title': 'تحليل بيانات العملات المشفرة',
        'select_pair': 'اختيار زوج العملة المشفرة',
        'select_interval': 'اختيار فترة زمنية',
        'lookback_period': 'فترة العودة (أيام)',
        'fetch_button': 'احصل على البيانات وقم بالتحليل',
        'data_error': 'تعذر استرداد البيانات. يرجى المحاولة مرة أخرى لاحقًا.',
        'last_price': 'آخر سعر',
        'expected_price': 'السعر المتوقع',
        'expected_increase_percentage': 'نسبة الزيادة المتوقعة',
        'buy_signals': 'إشارات الشراء',
        'sell_signals': 'إشارات البيع',
        'indicators': 'المؤشرات',
        'sma_50': 'SMA 50',
        'ema_50': 'EMA 50',
        'rsi': 'RSI',
        'macd_line': 'MACD الخط',
        'macd_signal': 'MACD الإشارة',
        'atr': 'ATR',
        'percent_k': '%K',
        'percent_d': '%D',
        'bollinger_upper': 'باند بولينجر (علوي)',
        'bollinger_lower': 'باند بولينجر (سفلي)',
        'chart_title': 'مخطط الأسعار',
        'expected_price_chart_title': 'مخطط السعر المتوقع'
    }
}

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
language = st.selectbox('Select Language / Dil Seçin', ['English', 'Turkish', 'Chinese', 'Hindi', 'Arabic'])

st.title(translations[language]['title'])

selected_pair = st.selectbox(translations[language]['select_pair'], USDT_PAIRS)
data_interval = st.selectbox(translations[language]['select_interval'], ['daily', 'hourly'])
lookback_period = st.slider(translations[language]['lookback_period'], min_value=30, max_value=365, value=90)

if st.button(translations[language]['fetch_button']):
    df = fetch_data(selected_pair, interval=data_interval, lookback=lookback_period)
    if df.empty:
        st.error(translations[language]['data_error'])
    else:
        df = calculate_indicators(df)
        df = generate_signals(df)
        forecast = forecast_next_price(df)
        expected_price, expected_increase_percentage = calculate_expected_price(df)
        
        st.write(f"**{translations[language]['last_price']}:** {df['close'].iloc[-1]}")
        st.write(f"**{translations[language]['expected_price']}:** {expected_price}")
        st.write(f"**{translations[language]['expected_increase_percentage']}:** {expected_increase_percentage:.2%}")
        st.write(f"**{translations[language]['buy_signals']}:** {df['Buy_Signal'].sum()} days")
        st.write(f"**{translations[language]['sell_signals']}:** {df['Sell_Signal'].sum()} days")
        
        st.write(f"### {translations[language]['indicators']}")
        st.write(f"**{translations[language]['sma_50']}:** {df['SMA_50'].iloc[-1]}")
        st.write(f"**{translations[language]['ema_50']}:** {df['EMA_50'].iloc[-1]}")
        st.write(f"**{translations[language]['rsi']}:** {df['RSI'].iloc[-1]}")
        st.write(f"**{translations[language]['macd_line']}:** {df['MACD_Line'].iloc[-1]}")
        st.write(f"**{translations[language]['macd_signal']}:** {df['MACD_Signal'].iloc[-1]}")
        st.write(f"**{translations[language]['atr']}:** {df['ATR'].iloc[-1]}")
        st.write(f"**{translations[language]['percent_k']}:** {df['%K'].iloc[-1]}")
        st.write(f"**{translations[language]['percent_d']}:** {df['%D'].iloc[-1]}")
        st.write(f"**{translations[language]['bollinger_upper']}:** {df['BB_Upper'].iloc[-1]}")
        st.write(f"**{translations[language]['bollinger_lower']}:** {df['BB_Lower'].iloc[-1]}")
        
        # Grafikleri oluşturma
        st.write(f"### {translations[language]['chart_title']}")
        fig, ax = plt.subplots()
        ax.plot(df.index, df['close'], label='Price')
        ax.plot(df.index, df['SMA_50'], label='SMA 50')
        ax.plot(df.index, df['EMA_50'], label='EMA 50')
        ax.plot(df.index, df['BB_Upper'], label='Bollinger Upper', linestyle='--')
        ax.plot(df.index, df['BB_Lower'], label='Bollinger Lower', linestyle='--')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title(translations[language]['chart_title'])
        ax.legend()
        st.pyplot(fig)
        
        st.write(f"### {translations[language]['expected_price_chart_title']}")
        fig, ax = plt.subplots()
        ax.plot(df.index, df['close'], label='Price')
        ax.axhline(y=expected_price, color='r', linestyle='--', label='Expected Price')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title(translations[language]['expected_price_chart_title'])
        ax.legend()
        st.pyplot(fig)
