import streamlit as st
import json
import os

JSON_FILE = "randevular.json"

# Verileri JSON dosyasından oku
def get_randevular():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r') as f:
        return json.load(f)

# Verileri güncelle
def update_randevu_status(randevu_id, durum):
    randevular = get_randevular()
    for randevu in randevular:
        if randevu['id'] == randevu_id:
            randevu['durum'] = durum
            break
    save_randevular(randevular)

# Verileri JSON dosyasına kaydet
def save_randevular(randevular):
    with open(JSON_FILE, 'w') as f:
        json.dump(randevular, f)

# Randevu yönetim paneli
def admin_page():
    st.title("Randevu Yönetim Paneli")
    
    randevular = get_randevular()
    
    if not randevular:
        st.warning("Henüz randevu alınmamış.")
        return
    
    for randevu in randevular:
        id, ad, telefon, tarih, saat, masaj_turu, durum = randevu["id"], randevu["ad"], randevu["telefon"], randevu["tarih"], randevu["saat"], randevu["masaj_turu"], randevu["durum"]
        with st.expander(f"{ad} - {tarih} {saat} ({masaj_turu}) [Durum: {durum}]"):
            st.write(f"**Telefon:** {telefon}")
            st.write(f"**Tarih:** {tarih}")
            st.write(f"**Saat:** {saat}")
            st.write(f"**Masaj Türü:** {masaj_turu}")
            
            if durum == "Beklemede":
                if st.button(f"Onayla ({id})"):
                    update_randevu_status(id, "Onaylandı")
                    st.experimental_rerun()
                if st.button(f"İptal Et ({id})"):
                    update_randevu_status(id, "İptal Edildi")
                    st.experimental_rerun()

            if st.button(f"Sil ({id})"):
                randevular = get_randevular()
                randevular = [r for r in randevular if r["id"] != id]
                save_randevular(randevular)
                st.experimental_rerun()

if __name__ == "__main__":
    admin_page()
