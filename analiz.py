
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

def calculate_profit_loss(entry_price, current_price, transaction_amount=50):
    if entry_price is None:
        return 0, transaction_amount  # If entry_price is None, cannot calculate profit/loss, return 0

    dollar_amount = transaction_amount / entry_price
    current_dollar_value = dollar_amount * current_price
    profit_loss = current_dollar_value - transaction_amount
    remaining_dollars = transaction_amount + profit_loss
    return profit_loss, remaining_dollars

def execute_trade(data, transaction_amount, last_signal_direction):
    buy_signals = data[data['Position'] == 1]
    sell_signals = data[data['Position'] == -1]
    
    if last_signal_direction == 'Long' and not st.session_state.get('in_trade', False):
        current_price = data.iloc[-1]['Close']
        st.write(f"Alım yapıldı. Güncel Fiyat: {current_price}")
        st.session_state['in_trade'] = True
        st.session_state['entry_price'] = current_price
        st.session_state['last_signal_direction'] = 'Long'
        
    elif last_signal_direction == 'Short' and st.session_state.get('in_trade', False):
        entry_price = st.session_state['entry_price']
        current_price = data.iloc[-1]['Close']
        profit_loss, remaining_dollars = calculate_profit_loss(entry_price, current_price, transaction_amount=transaction_amount)
        st.write(f"Satış yapıldı. Çıkış Fiyatı: {current_price}")
        if profit_loss >= 0:
            st.write(f"Toplam Kar: {profit_loss:.2f} USD (+{remaining_dollars:.2f} dolar)")
        else:
            st.write(f"Toplam Zarar: {profit_loss:.2f} USD (+{remaining_dollars:.2f} dolar)")
        st.session_state['in_trade'] = False
        st.session_state['entry_price'] = None
        st.session_state['last_signal_direction'] = None

# Streamlit application structure
st.title('Canlı Al/Sat Botu')

ticker = st.text_input('Hisse Senedi veya Kripto Para Ticker:', 'BTC-USD')
period = st.selectbox('Veri Periyodu:', ['1d', '1h', '1mo'], index=0)
interval = st.selectbox('Veri Aralığı:', ['1m', '5m', '15m', '30m', '1h'], index=0)

short_window = 20
long_window = 50

transaction_amount = st.number_input('İşlem Miktarı (Dolar)', min_value=0.0, value=50.0, step=10.0)

# Check if there is already an entry price and ticker in session state
if 'entry_price' not in st.session_state:
    st.session_state['entry_price'] = None

if 'last_signal_direction' not in st.session_state:
    st.session_state['last_signal_direction'] = None

if 'ticker_in_trade' not in st.session_state:
    st.session_state['ticker_in_trade'] = None

# Check if ticker has changed
if st.session_state['ticker_in_trade'] != ticker:
    st.session_state['ticker_in_trade'] = ticker  # Update ticker in trade session state

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
        st.session_state['last_signal_direction'] = 'Long'
    else:
        st.write(f"Sat Sinyali Tarihi: {last_sell_signal['Date']}")
        st.write(f"Giriş Fiyatı: {last_sell_signal['Close']} - Şuanki Fiyat: {data.iloc[-1]['Close']}")
        st.write(f"Stop Loss Seviyesi: {last_sell_signal['Close'] * 1.05}")
        st.write(f"Hedef Seviyesi: {last_sell_signal['Close'] * 0.9}")
        st.session_state['last_signal_direction'] = 'Short'

elif not buy_signals.empty:
    last_buy_signal = buy_signals.iloc[-1]
    st.write(f"Al Sinyali Tarihi: {last_buy_signal['Date']}")
    st.write(f"Giriş Fiyatı: {last_buy_signal['Close']} - Şuanki Fiyat: {data.iloc[-1]['Close']}")
    st.write(f"Stop Loss Seviyesi: {last_buy_signal['Close'] * 0.95}")
    st.write(f"Hedef Seviyesi: {last_buy_signal['Close'] * 1.1}")
    st.session_state['last_signal_direction'] = 'Long'

elif not sell_signals.empty:
    last_sell_signal = sell_signals.iloc[-1]
    st.write(f"Sat Sinyali Tarihi: {last_sell_signal['Date']}")
    st.write(f"Giriş Fiyatı: {last_sell_signal['Close']} - Şuanki Fiyat: {data.iloc[-1]['Close']}")
    st.write(f"Stop Loss Seviyesi: {last_sell_signal['Close'] * 1.05}")
    st.write(f"Hedef Seviyesi: {last_sell_signal['Close'] * 0.9}")
    st.session_state['last_signal_direction'] = 'Short'

else:
    st.write("Son al veya sat sinyali bulunamadı.")

# Execute trades based on signal direction
if st.session_state['last_signal_direction'] == 'Long' and not st.session_state.get('in_trade', False):
    execute_trade(data, transaction_amount, 'Long')

elif st.session_state['last_signal_direction'] == 'Short' and st.session_state.get('in_trade', False):
    execute_trade(data, transaction_amount, 'Short')

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

if st.session_state.get('in_trade', False):
    entry_price = st.session_state['entry_price']
    current_price = data.iloc[-1]['Close']
    profit_loss, remaining_dollars = calculate_profit_loss(entry_price, current_price, transaction_amount=transaction_amount)
    if profit_loss >= 0:
        st.write(f"Aktif İşlem: Giriş Fiyatı: {entry_price}, Şuanki Fiyat: {current_price}, Toplam Kar: {profit_loss:.2f} USD (+{remaining_dollars:.2f} dolar)")
    else:
        st.write(f"Aktif İşlem: Giriş Fiyatı: {entry_price}, Şuanki Fiyat: {current_price}, Toplam Zarar: {profit_loss:.2f} USD (+{remaining_dollars:.2f} dolar)")

# Automatically update every 60 seconds
while True:
    time.sleep(60)
    st.experimental_rerun()
