import streamlit as st
import sqlite3

def get_appointments():
    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, date, time, massage_type, status FROM appointments")
    data = cursor.fetchall()
    conn.close()
    return data

def update_appointment_status(appointment_id, status):
    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
    conn.commit()
    conn.close()

def delete_appointment(appointment_id):
    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()

def admin_page():
    st.title("Randevu Yönetim Paneli")
    
    appointments = get_appointments()
    
    if not appointments:
        st.warning("Henüz randevu alınmamış.")
        return
    
    for appointment in appointments:
        id, name, phone, date, time, massage_type, status = appointment
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
