import streamlit as st
import requests
import json
from datetime import datetime

# JSON dosya URL'si
JSON_URL = "https://masajostim.com.tr/randevular.json"

# Randevuları getir
def get_randevular():
    try:
        response = requests.get(JSON_URL)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Randevular yüklenirken hata oluştu: {str(e)}")
        return []

# Yeni randevu kaydetme
def save_randevu(ad, telefon, tarih, saat, masaj_turu):
    new_randevu = {
        "id": int(datetime.now().timestamp()),  # Benzersiz ID
        "ad": ad,
        "telefon": telefon,
        "tarih": str(tarih),
        "saat": str(saat),
        "masaj_turu": masaj_turu,
        "durum": "Beklemede"
    }
    
    try:
        # Mevcut randevuları al
        randevular = get_randevular()
        randevular.append(new_randevu)

        # JSON'a yaz
        headers = {'Content-Type': 'application/json'}
        response = requests.post(JSON_URL, data=json.dumps(randevular), headers=headers)
        
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Randevu kaydedilirken hata oluştu: {str(e)}")
        return False

# Randevu durumunu güncelleme
def update_randevu_status(randevu_id, yeni_durum):
    randevular = get_randevular()
    for randevu in randevular:
        if randevu["id"] == randevu_id:
            randevu["durum"] = yeni_durum
            break

    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(JSON_URL, data=json.dumps(randevular), headers=headers)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Durum güncellenirken hata oluştu: {str(e)}")
        return False

# Admin paneli
def admin_panel():
    st.title("📋 Randevu Yönetim Paneli")

    randevular = get_randevular()

    if not randevular:
        st.warning("Henüz randevu alınmamış.")
        return

    for randevu in randevular:
        id, ad, telefon, tarih, saat, masaj_turu, durum = (
            randevu["id"], randevu["ad"], randevu["telefon"], 
            randevu["tarih"], randevu["saat"], randevu["masaj_turu"], randevu["durum"]
        )
        with st.expander(f"📅 {tarih} - {saat} | {ad} ({masaj_turu}) [{durum}]"):
            st.write(f"**📞 Telefon:** {telefon}")
            
            if durum == "Beklemede":
                if st.button(f"✅ Onayla ({id})"):
                    update_randevu_status(id, "Onaylandı")
                    st.experimental_rerun()
                if st.button(f"❌ İptal Et ({id})"):
                    update_randevu_status(id, "İptal Edildi")
                    st.experimental_rerun()

# Randevu alma bölümü
def randevu_alma():
    st.title("💆‍♂️ Randevu Alma Sistemi")

    ad = st.text_input("Adınız ve Soyadınız")
    telefon = st.text_input("Telefon Numaranız")
    tarih = st.date_input("Randevu Tarihi", min_value=datetime.today())
    saat = st.time_input("Randevu Saati")
    masaj_turu = st.selectbox("Masaj Türü", ["Klasik Masaj (60 dk)", "Medikal Masaj (60 dk)", "Aromaterapi Masajı (60 dk)", "Thai Masajı", "Spor Masajı (50 dk)"])

    if st.button("📅 Randevu Al"):
        if ad and telefon:
            success = save_randevu(ad, telefon, tarih, saat, masaj_turu)
            if success:
                st.success("✅ Randevunuz başarıyla alındı!")
            else:
                st.error("❌ Randevu kaydedilirken hata oluştu.")
        else:
            st.error("⚠️ Lütfen tüm alanları doldurun.")

    # Mevcut randevuları göster
    st.subheader("📌 Mevcut Randevularınız")
    randevular = get_randevular()
    
    if randevular:
        for r in randevular:
            st.write(f"📅 {r['tarih']} 🕒 {r['saat']} - {r['masaj_turu']} ({r['durum']})")
    else:
        st.info("📭 Henüz randevunuz yok.")

# Sayfa seçimi
sayfa = st.sidebar.radio("📍 Sayfa Seçimi", ["Randevu Al", "Admin Paneli"])

if sayfa == "Randevu Al":
    randevu_alma()
else:
    admin_panel()
