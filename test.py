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

# Daha yüksek hassasiyet ayarlama
getcontext().prec = 50

# Binance API bağlantısı
exchange = ccxt.binanceus()

# Göstergeler için sabitler
RSI_TIME_PERIOD = 14
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9
BOLLINGER_WINDOW = 20
STOCH_FASTK_PERIOD = 14
STOCH_SLOWK_PERIOD = 3

def get_binance_data(symbol, interval, start_str, end_str):
    try:
        since = exchange.parse8601(start_str)
        klines = exchange.fetch_ohlcv(symbol, interval, since=since, limit=1000)
        if not klines or len(klines) < 51:
            return pd.DataFrame()
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']]
        df = df.astype(float)
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

def get_all_usdt_pairs():
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

def process_symbol(symbol, interval, start_str, end_str):
    df = get_binance_data(symbol, interval, start_str, end_str)
    if df.empty:
        return None

    try:
        df = calculate_indicators(df)
        df = generate_signals(df)
        forecast = forecast_next_price(df)
        expected_price, expected_increase_percentage = calculate_expected_price(df)
        entry_price, take_profit_price, stop_loss_price = calculate_trade_levels(df)
        
        if df['Buy_Signal'].iloc[-1] and expected_increase_percentage >= 5:
            return {
                'coin_name': symbol,
                'price': df['close'].iloc[-1],
                'expected_price': expected_price,
                'expected_increase_percentage': expected_increase_percentage,
                'sma_50': df['SMA_50'].iloc[-1],
                'rsi_14': df['RSI'].iloc[-1],
                'macd_line': df['MACD_Line'].iloc[-1],
                'macd_signal': df['MACD_Signal'].iloc[-1],
                'bb_upper': df['BB_Upper'].iloc[-1],
                'bb_middle': df['BB_Middle'].iloc[-1],
                'bb_lower': df['BB_Lower'].iloc[-1],
                'atr': df['ATR'].iloc[-1],
                'stoch_k': df['%K'].iloc[-1],
                'stoch_d': df['%D'].iloc[-1],
                'forecast_next_day_price': forecast,
                'entry_price': entry_price,
                'take_profit_price': take_profit_price,
                'stop_loss_price': stop_loss_price,
                'plot': plot_to_png(df, symbol)
            }
    except Exception as e:
        st.error(f"İşleme hatası ({symbol}): {e}")
        return None

def main():
    st.title('Kripto Para Analizi')
    
    interval = st.selectbox('Zaman Aralığı', ['4h'], index=0)  # 4 saatlik aralık seçimi
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=51)  # 51 gün geriye git
    start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')
    
    if st.button('Analiz Başlat'):
        usdt_pairs = get_all_usdt_pairs()
        if not usdt_pairs:
            st.error("USDT paritesi bulunamadı.")
            return
        
        total_pairs = len(usdt_pairs)
        st.write(f"Toplam çekilen parite sayısı: {total_pairs}")

        with ThreadPoolExecutor() as executor:
            future_to_symbol = {executor.submit(process_symbol, symbol, interval, start_str, end_str): symbol for symbol in usdt_pairs}
            results = []
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        st.write(f"Analiz edilen toplam coin sayısı: {len(results)}")
        
        for result in results:
            st.subheader(f"{result['coin_name']} Analizi")
            st.write(f"Mevcut Fiyat: ${result['price']:.10f}")
            st.write(f"Beklenen Fiyat: ${result['expected_price']:.10f}")
            st.write(f"Beklenen Artış Yüzdesi: {result['expected_increase_percentage']:.2f}%")
            st.write(f"SMA 50: ${result['sma_50']:.10f}")
            st.write(f"RSI 14: {result['rsi_14']:.2f}")
            st.write(f"MACD Line: {result['macd_line']:.10f}")
            st.write(f"MACD Signal: {result['macd_signal']:.10f}")
            st.write(f"BB Üst Bandı: ${result['bb_upper']:.10f}")
            st.write(f"BB Orta Bandı: ${result['bb_middle']:.10f}")
            st.write(f"BB Alt Bandı: ${result['bb_lower']:.10f}")
            st.write(f"ATR: {result['atr']:.10f}")
            st.write(f"Stochastic %K: {result['stoch_k']:.2f}")
            st.write(f"Stochastic %D: {result['stoch_d']:.2f}")
            st.write(f"Öngörülen Ertesi Gün Fiyatı: ${result['forecast_next_day_price']:.10f}")
            st.write(f"Giriş Fiyatı: ${result['entry_price']:.10f}")
            st.write(f"Kar Alma Fiyatı: ${result['take_profit_price']:.10f}")
            st.write(f"Zarar Durdur Fiyatı: ${result['stop_loss_price']:.10f}")
            st.image(f"data:image/png;base64,{result['plot']}", use_column_width=True)

if __name__ == '__main__':
    main()
