import streamlit as st
import sqlite3
from datetime import datetime

# Veritabanı bağlantısı
conn = sqlite3.connect("randevular.db", check_same_thread=False)
cursor = conn.cursor()

# Tablo oluşturma
cursor.execute('''
CREATE TABLE IF NOT EXISTS randevular (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isim TEXT,
    telefon TEXT,
    tarih TEXT,
    saat TEXT,
    masaj_turu TEXT,
    durum TEXT DEFAULT 'Beklemede'
)
''')
conn.commit()

# Kullanıcı arayüzü
st.title("Randevu Sistemi")
menu = ["Randevu Al", "Admin Paneli"]
secim = st.sidebar.selectbox("Menü", menu)

if secim == "Randevu Al":
    st.subheader("Randevu Al")
    isim = st.text_input("Adınız ve Soyadınız")
    telefon = st.text_input("Telefon Numaranız")
    tarih = st.date_input("Tarih Seçin", min_value=datetime.today())
    saat = st.time_input("Saat Seçin")
    masaj_turu = st.selectbox("Masaj Türü", ["Klasik Masaj", "Medikal Masaj", "Aromaterapi", "Derin Doku", "Spor Masajı"])
    
    if st.button("Randevu Al"):
        cursor.execute("INSERT INTO randevular (isim, telefon, tarih, saat, masaj_turu) VALUES (?, ?, ?, ?, ?)",
                       (isim, telefon, str(tarih), str(saat), masaj_turu))
        conn.commit()
        st.success("Randevunuz başarıyla alındı!")

elif secim == "Admin Paneli":
    st.subheader("Admin Paneli")
    admin_sifre = st.text_input("Admin Şifresi", type="password")
    if admin_sifre == "admin123":
        st.success("Giriş Başarılı!")
        
        randevular = cursor.execute("SELECT * FROM randevular").fetchall()
        for randevu in randevular:
            st.write(f"ID: {randevu[0]} | {randevu[1]} - {randevu[2]} - {randevu[3]} - {randevu[4]} - {randevu[5]} - Durum: {randevu[6]}")
            if st.button(f"Onayla {randevu[0]}"):
                cursor.execute("UPDATE randevular SET durum='Onaylandı' WHERE id=?", (randevu[0],))
                conn.commit()
                st.experimental_rerun()
            if st.button(f"İptal Et {randevu[0]}"):
                cursor.execute("DELETE FROM randevular WHERE id=?", (randevu[0],))
                conn.commit()
                st.experimental_rerun()
    else:
        st.warning("Yanlış şifre!")
