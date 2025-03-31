import streamlit as st
import json
import os
from datetime import datetime, time, timedelta

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
    new_randevu = {
        "ad": ad,
        "telefon": telefon,
        "tarih": str(tarih),
        "saat": str(saat),
        "masaj_turu": masaj_turu
    }
    st.session_state.randevular.append(new_randevu)
    save_randevular()

# 📌 Mevcut randevuları yükle
load_randevular()

# 📌 Kullanıcı randevu alma ekranı
st.markdown(
    """
    <style>
    body {
        font-size: 18px;
    }
    .stTextInput, .stDateInput, .stTimeInput, .stSelectbox {
        font-size: 20px !important;
    }
    .stButton button {
        width: 100%;
        padding: 15px;
        font-size: 20px;
    }
    .stSuccess, .stError {
        font-size: 18px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.title("📅 Randevu Alma Sistemi")

ad = st.text_input("Adınız ve Soyadınız")
telefon = st.text_input("Telefon Numaranız")
tarih = st.date_input("Randevu Tarihi", min_value=datetime.today())

# 📌 12:00 - 22:00 arasında her saat başı seçenekleri oluştur
baslangic_saat = time(12, 0)
bitis_saat = time(22, 0)
saatler = []
current_time = baslangic_saat

while current_time < bitis_saat:
    saatler.append(current_time.strftime("%H:%M"))
    current_time = (datetime.combine(datetime.today(), current_time) + timedelta(hours=1)).time()

# 📌 Daha önce alınan saatleri kaldır
alinan_saatler = [r["saat"] for r in st.session_state.randevular if r["tarih"] == str(tarih)]
uygun_saatler = [saat for saat in saatler if saat not in alinan_saatler]

# 📌 Bugünün tarihi seçildiyse, geçmiş saatleri kaldır
if tarih == datetime.today().date():
    simdiki_saat = datetime.now().time()
    uygun_saatler = [saat for saat in uygun_saatler if datetime.strptime(saat, "%H:%M").time() > simdiki_saat]

# 📌 Eğer tüm saatler doluysa
if not uygun_saatler:
    st.error("⚠️ Bu tarihte tüm saatler dolu veya geçmiş saatler kapalı! Lütfen başka bir gün seçin.")
else:
    saat = st.selectbox("Randevu Saati", uygun_saatler)
    masaj_turu = st.selectbox("Masaj Türü", ["Klasik Masaj (60 dk)", "Medikal Masaj (60 dk)", "Aromaterapi Masajı (60 dk)", "Thai Masajı", "Spor Masajı (50 dk)"])

    if st.button("📌 Randevu Al"):
        if ad and telefon:
            add_randevu(ad, telefon, tarih, saat, masaj_turu)
            st.success("✅ Randevunuz başarıyla alındı!")
            st.rerun()
        else:
            st.error("⚠️ Lütfen tüm alanları doldurun.")

# 📌 Mevcut randevuları listele
st.write("### 📌 Mevcut Randevularınız")
if st.session_state.randevular:
    for r in st.session_state.randevular:
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 10px; font-size: 18px;">
        📅 {r['tarih']} 🕒 {r['saat']} - {r['masaj_turu']}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("📭 Henüz randevunuz yok.")
