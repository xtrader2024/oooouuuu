import streamlit as st
import json
import os

JSON_FILE = "https://masajostim.com.tr/randevular.json"

# JSON dosyasından randevuları oku
def get_randevular():
    if not os.path.exists(JSON_FILE):
        return []
    
    try:
        with open(JSON_FILE, 'r') as f:
            randevular = json.load(f)
        return randevular
    except json.JSONDecodeError:
        return []  # Dosya bozuksa boş liste dön

# Randevu durumunu güncelle
def update_randevu_status(randevu_id, yeni_durum):
    randevular = get_randevular()
    
    for r in randevular:
        if r["id"] == randevu_id:
            r["durum"] = yeni_durum
            break
    
    with open(JSON_FILE, 'w') as f:
        json.dump(randevular, f)

# Randevuyu sil
def delete_randevu(randevu_id):
    randevular = get_randevular()
    
    # Seçilen randevuyu listeden kaldır
    randevular = [r for r in randevular if r["id"] != randevu_id]
    
    with open(JSON_FILE, 'w') as f:
        json.dump(randevular, f)

# Admin paneli
def admin_page():
    st.title("🛠️ Randevu Yönetim Paneli")

    randevular = get_randevular()

    if not randevular:
        st.warning("Henüz randevu alınmamış.")
        return

    for randevu in randevular:
        id, ad, telefon, tarih, saat, masaj_turu, durum = randevu["id"], randevu["ad"], randevu["telefon"], randevu["tarih"], randevu["saat"], randevu["masaj_turu"], randevu["durum"]
        
        with st.expander(f"📅 {tarih} 🕒 {saat} - {ad} ({masaj_turu}) [Durum: {durum}]"):
            st.write(f"📞 **Telefon:** {telefon}")
            st.write(f"📝 **Masaj Türü:** {masaj_turu}")

            # Beklemede olan randevular için işlem butonları
            if durum == "Beklemede":
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button(f"✅ Onayla {id}"):
                        update_randevu_status(id, "Onaylandı")
                        st.experimental_rerun()
                
                with col2:
                    if st.button(f"❌ İptal Et {id}"):
                        update_randevu_status(id, "İptal Edildi")
                        st.experimental_rerun()
                
                with col3:
                    if st.button(f"🗑️ Sil {id}"):
                        delete_randevu(id)
                        st.experimental_rerun()

if __name__ == "__main__":
    admin_page()
