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
