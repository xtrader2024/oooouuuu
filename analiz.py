import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# Define functions
def get_data(ticker, period='1d', interval='1m'):
    data = yf.download(ticker, period=period, interval=interval)
    data['Date'] = data.index
    data.reset_index(drop=True, inplace=True)
    return data

def calculate_signals(data, short_window=20, long_window=50):
    data['SMA_short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_long'] = data['Close'].rolling(window=long_window).mean()

    data['Signal'] = np.where(data['SMA_short'] > data['SMA_long'], 1, 0)
    data['Position'] = data['Signal'].diff()

    return data

# Streamlit application structure
st.title('Canlı Al/Sat Botu')

ticker = st.text_input('Hisse Senedi veya Kripto Para Ticker:', 'BTC-USD')
period = st.selectbox('Veri Periyodu:', ['1d', '1h', '1mo'], index=0)
interval = st.selectbox('Veri Aralığı:', ['1m', '5m', '15m', '30m', '1h'], index=0)

short_window = 20
long_window = 50

# Fetch and process data
data = get_data(ticker, period, interval)
data = calculate_signals(data, short_window, long_window)

st.write("Son Veri:")
st.dataframe(data.tail())

buy_signals = data[data['Position'] == 1]
sell_signals = data[data['Position'] == -1]

st.write("Son Sinyal:")
if not buy_signals.empty and not sell_signals.empty:
    last_buy_signal = buy_signals.iloc[-1]
    last_sell_signal = sell_signals.iloc[-1]
    
    if last_buy_signal['Date'] > last_sell_signal['Date']:
        st.write(f"Al Sinyali Tarihi: {last_buy_signal['Date']}")
        st.write(f"Giriş Fiyatı: {last_buy_signal['Close']} - Şuanki Fiyat: {data.iloc[-1]['Close']}")
        st.write(f"Stop Loss Seviyesi: {last_buy_signal['Close'] * 0.95}")
        st.write(f"Hedef Seviyesi: {last_buy_signal['Close'] * 1.1}")
    else:
        st.write(f"Sat Sinyali Tarihi: {last_sell_signal['Date']}")
        st.write(f"Giriş Fiyatı: {last_sell_signal['Close']} - Şuanki Fiyat: {data.iloc[-1]['Close']}")
        st.write(f"Stop Loss Seviyesi: {last_sell_signal['Close'] * 1.05}")
        st.write(f"Hedef Seviyesi: {last_sell_signal['Close'] * 0.9}")

elif not buy_signals.empty:
    last_buy_signal = buy_signals.iloc[-1]
    st.write(f"Al Sinyali Tarihi: {last_buy_signal['Date']}")
    st.write(f"Giriş Fiyatı: {last_buy_signal['Close']} - Şuanki Fiyat: {data.iloc[-1]['Close']}")
    st.write(f"Stop Loss Seviyesi: {last_buy_signal['Close'] * 0.95}")
    st.write(f"Hedef Seviyesi: {last_buy_signal['Close'] * 1.1}")

elif not sell_signals.empty:
    last_sell_signal = sell_signals.iloc[-1]
    st.write(f"Sat Sinyali Tarihi: {last_sell_signal['Date']}")
    st.write(f"Giriş Fiyatı: {last_sell_signal['Close']} - Şuanki Fiyat: {data.iloc[-1]['Close']}")
    st.write(f"Stop Loss Seviyesi: {last_sell_signal['Close'] * 1.05}")
    st.write(f"Hedef Seviyesi: {last_sell_signal['Close'] * 0.9}")

else:
    st.write("Son al veya sat sinyali bulunamadı.")

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(data['Date'], data['Close'], label='Kapanış Fiyatı')
ax.plot(data['Date'], data['SMA_short'], label=f'{short_window} Günlük SMA', linestyle='--')
ax.plot(data['Date'], data['SMA_long'], label=f'{long_window} Günlük SMA', linestyle='--')

ax.scatter(buy_signals['Date'], buy_signals['Close'], marker='^', color='g', label='Al Sinyali', s=100)
ax.scatter(sell_signals['Date'], sell_signals['Close'], marker='v', color='r', label='Sat Sinyali', s=100)

ax.set_xlabel('Tarih')
ax.set_ylabel('Fiyat')
ax.set_title(f'{ticker} Fiyat ve Sinyaller')
ax.legend()

st.pyplot(fig)

# Automatically update every 60 seconds
while True:
    time.sleep(60)
    st.experimental_rerun()
