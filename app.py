import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# =====================================================
# EMAIL CONFIG
# =====================================================
EMAIL_PENGIRIM = "jovitacw13@gmail.com"
EMAIL_PASSWORD = "hvrqmxxxxscajxbn"  # APP PASSWORD

def kirim_email(tujuan, nama_petugas, status, tanggal):
    if status == "SUDAH":
        isi = f"""
        ✅ Informasi Pengisian GForm Kebersihan

        Halo {nama_petugas},

        Terima kasih, Anda TELAH mengisi Google Form
        kebersihan kantor pada tanggal {tanggal}.

        Tetap pertahankan kedisiplinan 👍

        Salam,
        Sistem Monitoring Kebersihan
        """

        subject = f"Informasi Pengisian GForm - {nama_petugas}"

    else:
        isi = f"""
        ⚠️ Peringatan Pengisian GForm Kebersihan

        Halo {nama_petugas},

        Berdasarkan hasil monitoring sistem,
        Anda BELUM mengisi Google Form kebersihan
        pada tanggal {tanggal}.

        Mohon segera melakukan pengisian.

        Terima kasih.
        Sistem Monitoring Kebersihan
        """

        subject = f"Peringatan Pengisian GForm - {nama_petugas}"

    msg = MIMEText(isi)
    msg["Subject"] = subject
    msg["From"] = EMAIL_PENGIRIM
    msg["To"] = tujuan

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_PENGIRIM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# =====================================================
# MASTER PETUGAS & ZONA
# =====================================================
ZONA = {
    "Zona 1": ["Petugas Jaga"],
    "Zona 2": ["Salmin"],
    "Zona 3": ["Rudi"]
}

DAFTAR_PETUGAS = ["Petugas Jaga", "Salmin", "Rudi"]

# =====================================================
# LOAD DATA GFORM
# =====================================================
data = pd.read_csv("kebersihan.csv")
data["Tanggal"] = pd.to_datetime(data["Timestamp"]).dt.date

hari_ini = datetime.now().date()
data_today = data[data["Tanggal"] == hari_ini]

petugas_sudah_isi = (
    data_today["Nama"]
    .astype(str)
    .str.strip()
    .unique()
    .tolist()
)

petugas_belum_isi = [
    p for p in DAFTAR_PETUGAS if p not in petugas_sudah_isi
]

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(
    page_title="Monitoring Kebersihan Kantor",
    layout="wide"
)

# =====================================================
# LOGIN ADMIN
# =====================================================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login Admin")

    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.form_submit_button("Login"):
            if username == "admin" and password == "admin123":
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Username atau password salah")

    st.stop()

# =====================================================
# SIDEBAR MENU
# =====================================================
menu = st.sidebar.radio(
    "MENU",
    ["Beranda", "Detail Zona", "Notifikasi", "Logout"]
)

# =====================================================
# BERANDA
# =====================================================
if menu == "Beranda":
    st.title("📊 Monitoring Kebersihan Harian")
    st.info(f"📅 Tanggal: {hari_ini}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Petugas", len(DAFTAR_PETUGAS))
    col2.metric("Sudah Isi GForm", len(petugas_sudah_isi))
    col3.metric("Belum Isi GForm", len(petugas_belum_isi))

    st.divider()
    st.subheader("📋 Data Pengisian Hari Ini")
    st.dataframe(data_today, use_container_width=True)

# =====================================================
# DETAIL ZONA
# =====================================================
elif menu == "Detail Zona":
    st.title("🗺 Monitoring per Zona")

    for zona, petugas in ZONA.items():
        st.subheader(zona)
        for p in petugas:
            if p in petugas_sudah_isi:
                st.success(f"{p} — Sudah isi GForm")
            else:
                st.error(f"{p} — Belum isi GForm")

# =====================================================
# NOTIFIKASI
# =====================================================
elif menu == "Notifikasi":
    st.title("🚨 Notifikasi Monitoring")

    # 🔴 BELUM ISI
    if petugas_belum_isi:
        st.subheader("⚠️ Petugas Belum Mengisi GForm")
        for p in petugas_belum_isi:
            email = data[data["Nama"] == p]["Email"].iloc[-1]

            if st.button(f"Kirim Email Peringatan ke {p}", key=p):
                sukses = kirim_email(
                    email,
                    p,
                    status="BELUM",
                    tanggal=hari_ini
                )
                if sukses:
                    st.success(f"Email peringatan terkirim ke {p}")
                else:
                    st.error("Gagal mengirim email")

    else:
        st.success("🎉 Semua petugas sudah mengisi GForm hari ini")

# =====================================================
# LOGOUT
# =====================================================
elif menu == "Logout":
    st.session_state.login = False
    st.rerun()
