import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
import statsmodels.api as sm
import streamlit as st
from pycoingecko import CoinGeckoAPI

# CoinGecko API nesnesi oluşturuluyor
cg = CoinGeckoAPI()

# Göstergeler için sabitler
RSI_TIME_PERIOD = 14
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9
BOLLINGER_WINDOW = 20
STOCH_FASTK_PERIOD = 14
STOCH_SLOWK_PERIOD = 3

def get_coingecko_data(symbol, start_date, end_date):
    try:
        data = cg.get_coin_market_chart_range_range_range(id=symbol, vs_currency='usd', from_timestamp=start_date, to_timestamp=end_date)
        if not data or 'prices' not in data:
            return pd.DataFrame()
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df.rename(columns={'price': 'close'})
        df['open'] = df['close']
        df['high'] = df['close']
        df['low'] = df['close']
        df['volume'] = np.nan  # Volume data is not available in CoinGecko
        return df
    except Exception as e:
        st.error(f"Veri çekme hatası ({symbol}): {e}")
        return pd.DataFrame()

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
    expected_increase_percentage = ((expected_price - price) / price) * 100 - 1
    
    return expected_price, expected_increase_percentage

def calculate_trade_levels(df, entry_pct=0.02, take_profit_pct=0.05, stop_loss_pct=0.02):
    if df.empty:
        return np.nan, np.nan, np.nan
    
    entry_price = df['close'].iloc[-1]
    take_profit_price = entry_price * (1 + take_profit_pct)
    stop_loss_price = entry_price * (1 - stop_loss_pct)
    
    return entry_price, take_profit_price, stop_loss_price

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

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return img_base64

# Streamlit Arayüzü
st.title('Kripto Para Analizi')

# Kullanıcıdan zaman aralığı seçimi
interval = st.selectbox('Zaman Aralığı', ['1d', '7d', '30d', '90d', '365d'])

# Tarih aralığı hesaplanıyor
end_date = datetime.now()
start_date = end_date - timedelta(days=51)
start_timestamp = int(start_date.timestamp())
end_timestamp = int(end_date.timestamp())

# Kripto paralar için liste alınıyor
symbols = ['bitcoin', 'ethereum', 'cardano']  # Buraya CoinGecko'dan desteklenen diğer coinleri ekleyebilirsiniz

for symbol in symbols:
    st.subheader(f'{symbol.upper()} Analizi')

    df = get_coingecko_data(symbol, start_timestamp, end_timestamp)
    if df.empty:
        st.write("Veri alınamadı.")
        continue

    df = calculate_indicators(df)
    df = generate_signals(df)
    forecast = forecast_next_price(df)
    expected_price, expected_increase_percentage = calculate_expected_price(df)
    entry_price, take_profit_price, stop_loss_price = calculate_trade_levels(df)

    st.write(f'**Son Kapanış Fiyatı:** ${df["close"].iloc[-1]:.2f}')
    st.write(f'**Beklenen Fiyat:** ${expected_price:.2f}')
    st.write(f'**Beklenen Artış Yüzdesi:** {expected_increase_percentage:.2f}%')
    st.write(f'**Giriş Fiyatı:** ${entry_price:.2f}')
    st.write(f'**Kar Alma Fiyatı:** ${take_profit_price:.2f}')
    st.write(f'**Zarar Kes Fiyatı:** ${stop_loss_price:.2f}')

    plot_image = plot_to_png(df, symbol)
    st.image(f"data:image/png;base64,{plot_image}", use_column_width=True)
