import streamlit as st
import json
from datetime import datetime
import os

JSON_FILE = "randevular.json"

# JSON dosyasına randevu ekleme
def save_randevu(ad, telefon, tarih, saat, masaj_turu):
    if not os.path.exists(JSON_FILE):
        # Dosya yoksa, başlıkları da ekle
        with open(JSON_FILE, 'w') as f:
            json.dump([], f)
    
    try:
        # Verileri JSON dosyasından oku
        with open(JSON_FILE, 'r') as f:
            randevular = json.load(f)
    except json.JSONDecodeError:
        # JSON dosyası bozuksa, sıfırla
        randevular = []
        with open(JSON_FILE, 'w') as f:
            json.dump(randevular, f)

    # En son id'yi al
    last_id = randevular[-1]["id"] if randevular else 0
    new_id = last_id + 1
    new_randevu = {
        "id": new_id,
        "ad": ad,
        "telefon": telefon,
        "tarih": str(tarih),
        "saat": str(saat),
        "masaj_turu": masaj_turu,
        "durum": "Beklemede"
    }
    
    # Yeni randevuyu ekle
    randevular.append(new_randevu)
    
    with open(JSON_FILE, 'w') as f:
        json.dump(randevular, f)

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
if os.path.exists(JSON_FILE):
    try:
        with open(JSON_FILE, 'r') as f:
            randevular = json.load(f)
        
        if randevular:
            for r in randevular:
                st.write(f"📅 {r['tarih']} 🕒 {r['saat']} - {r['masaj_turu']} ({r['durum']})")
        else:
            st.info("Henüz randevunuz yok.")
    except json.JSONDecodeError:
        st.error("Veri dosyası bozuk. Lütfen yöneticinize başvurun.")
else:
    st.info("Henüz randevu kaydı yapılmamış.")
