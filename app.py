import streamlit as st
import json
import os
from datetime import datetime

JSON_FILE = "randevular.json"

# 📌 JSON verilerini yükle
def load_randevular():
    if "randevular" not in st.session_state:
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, 'r') as f:
                    st.session_state.randevular = json.load(f)
            except json.JSONDecodeError:
                st.session_state.randevular = []
        else:
            st.session_state.randevular = []

# 📌 Randevuları kaydet
def save_randevular():
    with open(JSON_FILE, 'w') as f:
        json.dump(st.session_state.randevular, f, indent=4)

# 📌 Yeni randevu ekleme
def add_randevu(ad, telefon, tarih, saat, masaj_turu):
    new_id = len(st.session_state.randevular) + 1
    new_randevu = {
        "id": new_id,
        "ad": ad,
        "telefon": telefon,
        "tarih": str(tarih),
        "saat": str(saat),
        "masaj_turu": masaj_turu,
        "durum": "Beklemede"
    }
    st.session_state.randevular.append(new_randevu)
    save_randevular()

# 📌 Randevu yönetim paneli
def admin_page():
    st.title("📋 Randevu Yönetim Paneli")

    if not st.session_state.randevular:
        st.warning("Henüz randevu alınmamış.")
        return

    for randevu in st.session_state.randevular:
        with st.expander(f"{randevu['ad']} - {randevu['tarih']} {randevu['saat']} ({randevu['masaj_turu']})"):
            st.write(f"**Telefon:** {randevu['telefon']}")
            st.write(f"**Durum:** {randevu['durum']}")

            if st.button(f"✅ Onayla {randevu['id']}", key=f"onay_{randevu['id']}"):
                randevu["durum"] = "Onaylandı"
                save_randevular()
                st.experimental_rerun()

            if st.button(f"❌ İptal Et {randevu['id']}", key=f"iptal_{randevu['id']}"):
                randevu["durum"] = "İptal Edildi"
                save_randevular()
                st.experimental_rerun()

            if st.button(f"🗑️ Sil {randevu['id']}", key=f"sil_{randevu['id']}"):
                st.session_state.randevular.remove(randevu)
                save_randevular()
                st.experimental_rerun()

# 📌 Kullanıcı randevu alma ekranı
def user_page():
    st.title("📅 Randevu Alma Sistemi")

    ad = st.text_input("Adınız ve Soyadınız")
    telefon = st.text_input("Telefon Numaranız")
    tarih = st.date_input("Randevu Tarihi", min_value=datetime.today())
    saat = st.time_input("Randevu Saati")
    masaj_turu = st.selectbox("Masaj Türü", ["Klasik Masaj (60 dk)", "Medikal Masaj (60 dk)", "Aromaterapi Masajı (60 dk)", "Thai Masajı", "Spor Masajı (50 dk)"])

    if st.button("📌 Randevu Al"):
        if ad and telefon:
            add_randevu(ad, telefon, tarih, saat, masaj_turu)
            st.success("✅ Randevunuz başarıyla alındı!")
        else:
            st.error("⚠️ Lütfen tüm alanları doldurun.")

    st.write("### 📌 Mevcut Randevularınız")
    if st.session_state.randevular:
        for r in st.session_state.randevular:
            st.write(f"📅 {r['tarih']} 🕒 {r['saat']} - {r['masaj_turu']} ({r['durum']})")
    else:
        st.info("📭 Henüz randevunuz yok.")

# 📌 Sayfa seçimi
load_randevular()
sayfa = st.sidebar.radio("Menü", ["Kullanıcı", "Admin"])
if sayfa == "Kullanıcı":
    user_page()
else:
    admin_page()
