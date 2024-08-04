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

# Define language options
def get_translations(language):
    translations = {
        'tr': {
            'title': 'Canlı Al/Sat Botu',
            'ticker_label': 'Hisse Senedi veya Kripto Para Ticker:',
            'period_label': 'Veri Periyodu:',
            'interval_label': 'Veri Aralığı:',
            'transaction_amount_label': 'İşlem Miktarı (Dolar)',
            'latest_data': 'Son Veri:',
            'latest_signal': 'Son Sinyal:',
            'buy_signal_date': 'Al Sinyali Tarihi:',
            'sell_signal_date': 'Sat Sinyali Tarihi:',
            'entry_price': 'Giriş Fiyatı:',
            'current_price': 'Şuanki Fiyat:',
            'stop_loss_level': 'Stop Loss Seviyesi:',
            'target_level': 'Hedef Seviyesi:',
            'no_signals': 'Son al veya sat sinyali bulunamadı.',
            'plot_title': 'Fiyat ve Sinyaller'
        },
        'en': {
            'title': 'Live Buy/Sell Bot',
            'ticker_label': 'Stock or Crypto Ticker:',
            'period_label': 'Data Period:',
            'interval_label': 'Data Interval:',
            'transaction_amount_label': 'Transaction Amount (USD)',
            'latest_data': 'Latest Data:',
            'latest_signal': 'Latest Signal:',
            'buy_signal_date': 'Buy Signal Date:',
            'sell_signal_date': 'Sell Signal Date:',
            'entry_price': 'Entry Price:',
            'current_price': 'Current Price:',
            'stop_loss_level': 'Stop Loss Level:',
            'target_level': 'Target Level:',
            'no_signals': 'No recent buy or sell signals found.',
            'plot_title': 'Price and Signals'
        },
        'zh': {
            'title': '实时买卖机器人',
            'ticker_label': '股票或加密货币代码:',
            'period_label': '数据周期:',
            'interval_label': '数据间隔:',
            'transaction_amount_label': '交易金额 (美元)',
            'latest_data': '最新数据:',
            'latest_signal': '最新信号:',
            'buy_signal_date': '买入信号日期:',
            'sell_signal_date': '卖出信号日期:',
            'entry_price': '入场价格:',
            'current_price': '当前价格:',
            'stop_loss_level': '止损水平:',
            'target_level': '目标水平:',
            'no_signals': '未找到最近的买入或卖出信号。',
            'plot_title': '价格和信号'
        },
        'hi': {
            'title': 'लाइव बाय/सेल बॉट',
            'ticker_label': 'स्टॉक या क्रिप्टो टिकर:',
            'period_label': 'डेटा अवधि:',
            'interval_label': 'डेटा अंतराल:',
            'transaction_amount_label': 'लेन-देन राशि (USD)',
            'latest_data': 'नवीनतम डेटा:',
            'latest_signal': 'नवीनतम सिग्नल:',
            'buy_signal_date': 'खरीद सिग्नल तिथि:',
            'sell_signal_date': 'बेचने सिग्नल तिथि:',
            'entry_price': 'प्रवेश मूल्य:',
            'current_price': 'वर्तमान मूल्य:',
            'stop_loss_level': 'स्टॉप लॉस स्तर:',
            'target_level': 'लक्ष्य स्तर:',
            'no_signals': 'कोई हालिया खरीद या बिक्री सिग्नल नहीं मिला।',
            'plot_title': 'मूल्य और सिग्नल'
        },
        'ar': {
            'title': 'روبوت شراء/بيع مباشر',
            'ticker_label': 'رمز السهم أو العملة المشفرة:',
            'period_label': 'فترة البيانات:',
            'interval_label': 'فاصل البيانات:',
            'transaction_amount_label': 'مقدار الصفقة (دولار)',
            'latest_data': 'آخر البيانات:',
            'latest_signal': 'أحدث إشارة:',
            'buy_signal_date': 'تاريخ إشارة الشراء:',
            'sell_signal_date': 'تاريخ إشارة البيع:',
            'entry_price': 'سعر الدخول:',
            'current_price': 'السعر الحالي:',
            'stop_loss_level': 'مستوى وقف الخسارة:',
            'target_level': 'مستوى الهدف:',
            'no_signals': 'لم يتم العثور على إشارات شراء أو بيع حديثة.',
            'plot_title': 'السعر والإشارات'
        }
    }
    return translations.get(language, translations['en'])

# Streamlit application structure
language = st.selectbox('Dil Seçin:', ['tr', 'en', 'zh', 'hi', 'ar'], index=0)
translations = get_translations(language)

st.title(translations['title'])

ticker = st.text_input(translations['ticker_label'], 'BTC-USD')
period = st.selectbox(translations['period_label'], ['1d', '1h', '1mo'], index=0)
interval = st.selectbox(translations['interval_label'], ['1m', '5m', '15m', '30m', '1h'], index=0)

short_window = 20
long_window = 50

# Fetch and process data
data = get_data(ticker, period, interval)
data = calculate_signals(data, short_window, long_window)

st.write(translations['latest_data'])
st.dataframe(data.tail())

buy_signals = data[data['Position'] == 1]
sell_signals = data[data['Position'] == -1]

st.write(translations['latest_signal'])
if not buy_signals.empty and not sell_signals.empty:
    last_buy_signal = buy_signals.iloc[-1]
    last_sell_signal = sell_signals.iloc[-1]
    
    if last_buy_signal['Date'] > last_sell_signal['Date']:
        st.write(f"{translations['buy_signal_date']} {last_buy_signal['Date']}")
        st.write(f"{translations['entry_price']} {last_buy_signal['Close']} - {translations['current_price']} {data.iloc[-1]['Close']}")
        st.write(f"{translations['stop_loss_level']} {last_buy_signal['Close'] * 0.95}")
        st.write(f"{translations['target_level']} {last_buy_signal['Close'] * 1.1}")
    else:
        st.write(f"{translations['sell_signal_date']} {last_sell_signal['Date']}")
        st.write(f"{translations['entry_price']} {last_sell_signal['Close']} - {translations['current_price']} {data.iloc[-1]['Close']}")
        st.write(f"{translations['stop_loss_level']} {last_sell_signal['Close'] * 1.05}")
        st.write(f"{translations['target_level']} {last_sell_signal['Close'] * 0.9}")

elif not buy_signals.empty:
    last_buy_signal = buy_signals.iloc[-1]
    st.write(f"{translations['buy_signal_date']} {last_buy_signal['Date']}")
    st.write(f"{translations['entry_price']} {last_buy_signal['Close']} - {translations['current_price']} {data.iloc[-1]['Close']}")
    st.write(f"{translations['stop_loss_level']} {last_buy_signal['Close'] * 0.95}")
    st.write(f"{translations['target_level']} {last_buy_signal['Close'] * 1.1}")

elif not sell_signals.empty:
    last_sell_signal = sell_signals.iloc[-1]
    st.write(f"{translations['sell_signal_date']} {last_sell_signal['Date']}")
    st.write(f"{translations['entry_price']} {last_sell_signal['Close']} - {translations['current_price']} {data.iloc[-1]['Close']}")
    st.write(f"{translations['stop_loss_level']} {last_sell_signal['Close'] * 1.05}")
    st.write(f"{translations['target_level']} {last_sell_signal['Close'] * 0.9}")

else:
    st.write(translations['no_signals'])

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(data['Date'], data['Close'], label='Close Price')
ax.plot(data['Date'], data['SMA_short'], label=f'{short_window} Day SMA', linestyle='--')
ax.plot(data['Date'], data['SMA_long'], label=f'{long_window} Day SMA', linestyle='--')

ax.scatter(buy_signals['Date'], buy_signals['Close'], marker='^', color='g', label='Buy Signal', s=100)
ax.scatter(sell_signals['Date'], sell_signals['Close'], marker='v', color='r', label='Sell Signal', s=100)

ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.set_title(translations['plot_title'])
ax.legend()

st.pyplot(fig)

# Automatically update every 60 seconds
while True:
    time.sleep(60)
    st.experimental_rerun()
