import streamlit as st
import pandas as pd
import os

CSV_FILE = "appointments.csv"

def get_appointments():
    """CSV dosyasından randevuları oku"""
    if not os.path.exists(CSV_FILE):
        return []
    
    df = pd.read_csv(CSV_FILE)
    return df.to_dict(orient="records")

def save_appointments(appointments):
    """Randevuları CSV dosyasına kaydet"""
    df = pd.DataFrame(appointments)
    df.to_csv(CSV_FILE, index=False)

def update_appointment_status(appointment_id, status):
    """Belirtilen randevunun durumunu güncelle"""
    appointments = get_appointments()
    for appointment in appointments:
        if appointment["id"] == appointment_id:
            appointment["status"] = status
            break
    save_appointments(appointments)

def delete_appointment(appointment_id):
    """Belirtilen randevuyu sil"""
    appointments = get_appointments()
    appointments = [appt for appt in appointments if appt["id"] != appointment_id]
    save_appointments(appointments)

def admin_page():
    st.title("Randevu Yönetim Paneli")
    
    appointments = get_appointments()
    
    if not appointments:
        st.warning("Henüz randevu alınmamış.")
        return
    
    for appointment in appointments:
        id, name, phone, date, time, massage_type, status = (
            appointment["id"],
            appointment["name"],
            appointment["phone"],
            appointment["date"],
            appointment["time"],
            appointment["massage_type"],
            appointment["status"]
        )

        with st.expander(f"{name} - {date} {time} ({massage_type}) [Durum: {status}]"):
            st.write(f"**Telefon:** {phone}")
            st.write(f"**Tarih:** {date}")
            st.write(f"**Saat:** {time}")
            st.write(f"**Masaj Türü:** {massage_type}")
            
            if status == "Beklemede":
                if st.button("Onayla", key=f"approve_{id}"):
                    update_appointment_status(id, "Onaylandı")
                    st.experimental_rerun()
                if st.button("İptal Et", key=f"cancel_{id}"):
                    update_appointment_status(id, "İptal Edildi")
                    st.experimental_rerun()
            
            if st.button("Sil", key=f"delete_{id}"):
                delete_appointment(id)
                st.experimental_rerun()

if __name__ == "__main__":
    admin_page()
