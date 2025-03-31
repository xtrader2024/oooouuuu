import streamlit as st
from datetime import datetime, timedelta
import webbrowser

# Sayfa başlığı
st.title("Bilgi ve Rezervasyon")

# Şube bilgileri
selected_branch = "Ostim - Batıkent Şube"
st.subheader(selected_branch)
st.write("Harika bir masaj deneyimi için doğru adrestesiniz! Ostim ve Batıkent’e yalnızca birkaç dakika uzaklıkta, özel merkezimizde profesyonel masaj hizmetleri sunmaktayız. Hamam hizmetleri ve kese köpük hizmetimiz yoktur. Odalarımızda duş kabini bulunmaktadır.")
st.write("Çalışma Saatleri: 12:00 - 21:00")
st.write("Adres: Ostim, Alınteri Blv. Ostim İş Merkezleri A Blok No:25 Kat: 4 Daire 33, 06374 Yenimahalle/Ankara")

# Google Maps bağlantısı
if st.button("Konum Göster"):
    webbrowser.open("https://www.google.com/search?q=fizyomasaj+ostim")

# Masaj paketleri
st.subheader("Masaj Paketleri")
packages = [
    {"name": "Klasik Masaj (60 dk)", "price": "990 ₺", "description": "Vücudu rahatlatan geleneksel masaj."},
    {"name": "Klasik Masaj (90 dk)", "price": "1400 ₺", "description": "Uzun süreli rahatlama sağlayan klasik masaj."},
    {"name": "Medikal Masaj (60 dk)", "price": "1400 ₺", "description": "Kasları derinlemesine rahatlatan masaj."},
    {"name": "Mix Terapi (60 dk)", "price": "1400 ₺", "description": "Sıcak taş, antistres ve klasik masaj karışımı."}
]

# Paketleri listeleme
selected_package = st.selectbox("Masaj Paketinizi Seçin", [p["name"] for p in packages])
selected_price = next(p["price"] for p in packages if p["name"] == selected_package)
st.write(f"Seçilen Paket: **{selected_package}**")
st.write(f"Fiyat: **{selected_price}**")

# Randevu tarihi ve saati seçimi
default_date = datetime.today() + timedelta(days=1)
selected_date = st.date_input("Randevu Tarihi Seçin", min_value=datetime.today(), value=default_date)
selected_time = st.time_input("Randevu Saati Seçin", value=datetime.strptime("12:00", "%H:%M").time())

# WhatsApp ile rezervasyon
def generate_whatsapp_message():
    message = (f"Merhaba, {selected_branch} şubesinden {selected_package} paketi için "
               f"{selected_date} tarihinde saat {selected_time.strftime('%H:%M')} için randevu almak istiyorum."
               " Lütfen bana dönüş yapar mısınız?")
    return message.replace(" ", "%20")

if st.button("WhatsApp ile Randevu Talep Et"):
    whatsapp_url = f"https://wa.me/905305647326?text={generate_whatsapp_message()}"
    webbrowser.open(whatsapp_url)

if st.button("Web Sitesine Git"):
    webbrowser.open("https://masajostim.com.tr")
