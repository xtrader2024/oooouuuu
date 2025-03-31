import streamlit as st
import pandas as pd

# Sayfa başlığı
st.set_page_config(page_title="Bilgi ve Rezervasyon", layout="centered")

# Şube bilgileri
st.markdown("## Harika bir masaj deneyimi için doğru adrestesiniz!")
st.markdown(
    "Ostim ve Batıkent’e yalnızca birkaç dakika uzaklıkta, Alınteri Bulvarı’ndaki özel merkezimizde "
    "Bayan ve Bay ekibimiz ile profesyonel masaj hizmetleri sunmaktayız. Hamam hizmetleri ve kese köpük hizmetimiz yoktur. "
    "Odalarımızda duş kabini bulunmaktadır."
)
st.markdown("**Çalışma Saatleri:** 12:00 - 21:00")
st.markdown("**Adres:** Ostim, Alınteri Blv. Ostim İş Merkezleri A Blok No:25 Kat: 4 Daire 33, 06374 Yenimahalle/Ankara")

if st.button("Konum Göster"):
    st.markdown("[Google Haritalar'da Aç](https://www.google.com/search?q=fizyomasaj+ostim)")

# Masaj paketleri
st.markdown("## Masaj Paketleri")

packages = [
    {"name": "Klasik Masaj (60 dk)", "price": "990 ₺", "desc": "Geleneksel masaj, stres azaltır ve kasları gevşetir. 12'li paket fiyatı: 10.000 ₺"},
    {"name": "Klasik Masaj (90 dk)", "price": "1400 ₺", "desc": "Uzun süreli rahatlama sağlayan klasik masaj."},
    {"name": "Medikal Masaj (60 dk)", "price": "1400 ₺", "desc": "Ağrı giderici özel teknikler kullanan masaj."},
    {"name": "Mix Terapi (60 dk)", "price": "1400 ₺", "desc": "Sıcak taş, antistres ve klasik masaj kombinasyonu."},
    {"name": "Aromaterapi Masajı (60 dk)", "price": "1200 ₺", "desc": "Aromatik yağlarla yapılan rahatlatıcı masaj."},
    {"name": "Ayak Masajı (30 dk)", "price": "600 ₺", "desc": "Refleksoloji teknikleriyle yapılan rahatlatıcı ayak masajı."},
]

df = pd.DataFrame(packages)
selected_package = st.selectbox("Bir masaj paketi seçin:", df["name"].tolist())

if selected_package:
    package_info = df[df["name"] == selected_package].iloc[0]
    st.markdown(f"**Fiyat:** {package_info['price']}")
    st.markdown(f"**Açıklama:** {package_info['desc']}")

# Randevu butonları
st.markdown("## Randevu Talep Et")
col1, col2 = st.columns(2)
with col1:
    if st.button("WhatsApp'a Devam Et", key="whatsapp"):
        st.markdown("[WhatsApp'tan Randevu Al](https://wa.me/905305647326)")
with col2:
    if st.button("Web Sitesine Devam Et", key="website"):
        st.markdown("[Web Sitesine Git](https://masajostim.com.tr)")

# Takvim iframe
st.markdown("## Online Randevu Takvimi")
st.components.v1.html(
    '<iframe src="https://www.calengoo.com/booking/fizyomasaj/#/" width="100%" height="700px" frameborder="0"></iframe>',
    height=700
)
