import streamlit as st
import pandas as pd
from datetime import datetime
import os

CSV_FILE = "randevular.csv"

# CSV dosyasına randevu ekleme
def save_randevu(ad, telefon, tarih, saat, masaj_turu):
    if not os.path.exists(CSV_FILE):
        # Dosya yoksa, başlıkları da ekle
        df = pd.DataFrame(columns=["id", "ad", "telefon", "tarih", "saat", "masaj_turu", "durum"])
        df.to_csv(CSV_FILE, index=False)
    
    # En son id'yi al
    df = pd.read_csv(CSV_FILE)
    last_id = df["id"].max() if not df.empty else 0
    
    new_id = last_id + 1
    new_randevu = pd.DataFrame([[new_id, ad, telefon, tarih, saat, masaj_turu, "Beklemede"]],
                               columns=["id", "ad", "telefon", "tarih", "saat", "masaj_turu", "durum"])
    
    # Yeni randevuyu ekle
    df = pd.concat([df, new_randevu], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# Randevu alma kısmı
st.title("Randevu Alma Sistemi")

ad = st.text_input("Adınız ve Soyadınız")
telefon = st.text_input("Telefon Numaranız")
tarih = st.date_input("Randevu Tarihi", min_value=datetime.today())
saat = st.time_input("Randevu Saati")
masaj_turu = st.selectbox("Masaj Türü", ["Klasik Masaj (60 dk)", "Medikal Masaj (60 dk)", "Aromaterapi Masajı (60 dk)", "Thai Masajı", "Spor Masajı (50 dk)"])

if st.button("Randevu Al"):
    if ad and telefon:
        save_randevu(ad, telefon, tarih, saat, masaj_turu)
        st.success("Randevunuz başarıyla alındı!")
    else:
        st.error("Lütfen tüm alanları doldurun.")

# Mevcut randevuları gösterme
st.write("**Mevcut Randevularınız**")
if os.path.exists(CSV_FILE):
    randevular = pd.read_csv(CSV_FILE)
    randevular_display = randevular[["tarih", "saat", "masaj_turu", "durum"]]
    if not randevular_display.empty:
        for _, r in randevular_display.iterrows():
            st.write(f"📅 {r['tarih']} 🕒 {r['saat']} - {r['masaj_turu']} ({r['durum']})")
    else:
        st.info("Henüz randevunuz yok.")
else:
    st.info("Henüz randevu kaydı yapılmamış.")
