import streamlit as st
import pandas as pd
from datetime import datetime
import os

CSV_FILE = "randevular.csv"

# Verileri CSV dosyasından oku
def get_randevular():
    if not os.path.exists(CSV_FILE):
        return []
    df = pd.read_csv(CSV_FILE)
    return df.to_dict(orient="records")

# Verileri CSV dosyasına kaydet
def save_randevular(randevular):
    df = pd.DataFrame(randevular)
    df.to_csv(CSV_FILE, index=False)

st.title("Randevu Alma Sistemi")

ad = st.text_input("Adınız ve Soyadınız")
telefon = st.text_input("Telefon Numaranız")
tarih = st.date_input("Randevu Tarihi", min_value=datetime.today())
saat = st.time_input("Randevu Saati")
masaj_turu = st.selectbox("Masaj Türü", ["Klasik Masaj (60 dk)", "Medikal Masaj (60 dk)", "Aromaterapi Masajı (60 dk)", "Thai Masajı", "Spor Masajı (50 dk)"])

if st.button("Randevu Al"):
    if ad and telefon:
        randevular = get_randevular()
        new_id = len(randevular) + 1  # Yeni ID, mevcut randevulardan biriyle çakışmasın diye
        new_randevu = {
            "id": new_id,
            "ad": ad,
            "telefon": telefon,
            "tarih": str(tarih),
            "saat": str(saat),
            "masaj_turu": masaj_turu,
            "durum": "Beklemede"
        }
        randevular.append(new_randevu)
        save_randevular(randevular)
        st.success("Randevunuz başarıyla alındı!")
    else:
        st.error("Lütfen tüm alanları doldurun.")

# Mevcut randevuları göster
st.write("**Mevcut Randevularınız**")
randevular = get_randevular()
if randevular:
    for r in randevular:
        st.write(f"📅 {r['tarih']} 🕒 {r['saat']} - {r['masaj_turu']} ({r['durum']})")
else:
    st.info("Henüz randevunuz yok.")
import streamlit as st
import sqlite3
from datetime import datetime

# Veritabanı bağlantısı
conn = sqlite3.connect("randevular.db", check_same_thread=False)
c = conn.cursor()

# Randevu tablosunu oluşturma
c.execute('''CREATE TABLE IF NOT EXISTS randevular
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              ad TEXT, 
              telefon TEXT, 
              tarih TEXT, 
              saat TEXT, 
              masaj_turu TEXT, 
              durum TEXT DEFAULT 'Beklemede')''')
conn.commit()

st.title("Randevu Alma Sistemi")

ad = st.text_input("Adınız ve Soyadınız")
telefon = st.text_input("Telefon Numaranız")
tarih = st.date_input("Randevu Tarihi", min_value=datetime.today())
saat = st.time_input("Randevu Saati")
masaj_turu = st.selectbox("Masaj Türü", ["Klasik Masaj (60 dk)", "Medikal Masaj (60 dk)", "Aromaterapi Masajı (60 dk)", "Thai Masajı", "Spor Masajı (50 dk)"])

if st.button("Randevu Al"):
    if ad and telefon:
        c.execute("INSERT INTO randevular (ad, telefon, tarih, saat, masaj_turu) VALUES (?, ?, ?, ?, ?)", (ad, telefon, tarih, saat, masaj_turu))
        conn.commit()
        st.success("Randevunuz başarıyla alındı!")
    else:
        st.error("Lütfen tüm alanları doldurun.")

st.write("**Mevcut Randevularınız**")
randevular = c.execute("SELECT tarih, saat, masaj_turu, durum FROM randevular").fetchall()
if randevular:
    for r in randevular:
        st.write(f"📅 {r[0]} 🕒 {r[1]} - {r[2]} ({r[3]})")
else:
    st.info("Henüz randevunuz yok.")
