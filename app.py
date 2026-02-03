import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# =====================================================
# EMAIL CONFIG
# =====================================================
EMAIL_PENGIRIM = "jovitacw13@gmail.com"
EMAIL_PASSWORD = "hvrqmxxxxscajxbn"

def kirim_email(tujuan, nama_petugas, status, tanggal):
    if status == "BELUM":
        subject = f"⚠️ Peringatan Belum Mengisi GForm – {nama_petugas}"
        isi = f"""
Halo {nama_petugas},

Anda BELUM mengisi Google Form kebersihan
pada tanggal {tanggal}.

Mohon segera melakukan pengisian.

Terima kasih.
"""
    else:
        subject = f"⚠️ Checklist Kebersihan Tidak Lengkap – {nama_petugas}"
        isi = f"""
Halo {nama_petugas},

Anda sudah mengisi Google Form kebersihan
pada tanggal {tanggal}, namun terdapat
checklist ruangan yang BELUM lengkap
di zona tanggung jawab Anda.

Mohon segera dilengkapi.

Terima kasih.
"""

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
# MASTER ZONA
# =====================================================
ZONA = {
    "Zona 1": [
        "Ruang Rapat Kecil",
        "Ruang Resepsionis dan Pintu Masuk",
        "Ruang PST",
        "Halaman Depan"
    ],
    "Zona 2": [
        "Ruang Laktasi",
        "Toilet Pengunjung",
        "Ruang Harmoni (Rapat Besar)",
        "Ruang Tata Usaha",
        "Halaman Belakang"
    ],
    "Zona 3": [
        "Ruang Pengolahan",
        "Ruang Pantri & Toilet pegawai",
        "Ruang Dinamis (flexible area)",
        "Ruang Mushola",
        "Ruang Arsip",
        "Ruang Gudang",
        "Halaman Samping"
    ]
}

# =====================================================
# PETUGAS PENANGGUNG JAWAB ZONA
# =====================================================
PETUGAS_ZONA = {
    "Petugas Jaga": "Zona 1",
    "Salmin": "Zona 2",
    "Rudi": "Zona 3"
}

# =====================================================
# LOAD DATA
# =====================================================
data = pd.read_csv("gform1.csv")
data["Tanggal"] = pd.to_datetime(data["Timestamp"]).dt.date
hari_ini = datetime.now().date()

# =====================================================
# HELPER STATUS
# =====================================================
def cek_status_ruangan(value):
    return "✅ Lengkap" if pd.notna(value) else "❌ Tidak Lengkap"

def status_petugas(row):
    nama = row["Nama Petugas"]
    zona = PETUGAS_ZONA.get(nama)

    if not zona:
        return "TIDAK TERDAFTAR"

    ruangan_zona = ZONA[zona]
    return (
        "LENGKAP"
        if row[ruangan_zona].notna().all()
        else "TIDAK LENGKAP"
    )

data["Status Ruangan"] = data.apply(status_petugas, axis=1)

# =====================================================
# PETUGAS HARI INI
# =====================================================
DAFTAR_PETUGAS = sorted(data["Nama Petugas"].dropna().unique().tolist())
data_today = data[data["Tanggal"] == hari_ini]

petugas_sudah_isi = data_today["Nama Petugas"].unique().tolist()
petugas_belum_isi = [p for p in PETUGAS_ZONA if p not in petugas_sudah_isi]

# =====================================================
# LOGIN
# =====================================================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.set_page_config(
        page_title="Login Admin",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
    }

    .login-box {
        width: 360px;
        padding: 30px;
        border-radius: 14px;
        background-color: #0e1117;
        box-shadow: 0px 0px 30px rgba(0,0,0,0.7);
    }

    .login-title {
        text-align: center;
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 20px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # === SPACER ATAS (INI KUNCI NYA) ===
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Login Admin</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if username == "admin" and password == "admin123":
                    st.session_state.login = True
                    st.rerun()
                else:
                    st.error("Username atau password salah")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# =====================================================
# MENU
# =====================================================
if "menu" not in st.session_state:
    st.session_state.menu = "Beranda"

st.sidebar.title("MENU")
for m in ["Beranda", "Detail Zona", "Notifikasi", "Logout"]:
    if st.sidebar.button(m, use_container_width=True):
        st.session_state.menu = m

menu = st.session_state.menu

# =====================================================
# BERANDA
# =====================================================
if menu == "Beranda":
    st.title("📊 Monitoring Kebersihan")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Petugas", len(PETUGAS_ZONA))
    c2.metric("Sudah Isi Hari Ini", len(petugas_sudah_isi))
    c3.metric("Belum Isi Hari Ini", len(petugas_belum_isi))

    df = data[["Nama Petugas", "Email Petugas", "Tanggal", "Status Ruangan"]]
    df.insert(0, "No", range(1, len(df) + 1))
    st.dataframe(df, use_container_width=True, hide_index=True)

# =====================================================
# DETAIL ZONA
# =====================================================
elif menu == "Detail Zona":
    st.title("🗺 Detail Checklist per Zona")

    zona_pilih = st.selectbox("Pilih Zona", list(ZONA.keys()))

    rows = []
    for _, row in data.iterrows():
        if PETUGAS_ZONA.get(row["Nama Petugas"]) != zona_pilih:
            continue

        for ruang in ZONA[zona_pilih]:
            rows.append({
                "Nama Petugas": row["Nama Petugas"],
                "Tanggal": row["Tanggal"],
                "Ruangan": ruang,
                "Status": cek_status_ruangan(row.get(ruang))
            })

    df_zona = pd.DataFrame(rows)
    df_zona.insert(0, "No", range(1, len(df_zona) + 1))
    st.dataframe(df_zona, use_container_width=True, hide_index=True)

# =====================================================
# NOTIFIKASI
# =====================================================
elif menu == "Notifikasi":
    st.title("🚨 Notifikasi")
    st.caption("Email peringatan untuk petugas yang belum mengisi atau checklist belum lengkap")

    nomor = 1

    # =========================================
    # 1️⃣ PETUGAS BELUM ISI GFORM
    # =========================================
    st.subheader("❌ Belum Mengisi GForm Hari Ini")

    for p in petugas_belum_isi:
        # ambil email TERAKHIR petugas tsb (bukan hari ini)
        df_petugas = data[data["Nama Petugas"] == p]

        if df_petugas.empty:
            continue  # jaga-jaga kalau beneran ga ada sama sekali

        email = df_petugas["Email Petugas"].iloc[-1]

        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### {nomor}. {p}")
                st.error("Status: BELUM mengisi GForm")
                st.write(f"📅 Tanggal: {hari_ini}")

            with col2:
                st.write("")
                st.write("")
                if st.button("Kirim Email", key=f"belum_{p}"):
                    sukses = kirim_email(
                        email,
                        p,
                        "BELUM",
                        hari_ini
                    )
                    st.success("Email terkirim") if sukses else st.error("Gagal kirim email")

        nomor += 1

    # =========================================
    # 2️⃣ SUDAH ISI TAPI CHECKLIST TIDAK LENGKAP
    # =========================================
    st.subheader("⚠️ Checklist Zona Tidak Lengkap")

    for _, row in data_today.iterrows():
        if row["Status Ruangan"] != "TIDAK LENGKAP":
            continue

        nama = row["Nama Petugas"]
        zona = PETUGAS_ZONA.get(nama)

        if not zona:
            continue

        ruangan_belum = [
            r for r in ZONA[zona]
            if cek_status_ruangan(row.get(r)) == "❌ Tidak Lengkap"
        ]

        if not ruangan_belum:
            continue

        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### {nomor}. {nama}")
                st.warning(f"Zona: {zona}")
                st.write(f"📅 Tanggal: {row['Tanggal']}")
                st.write("**Ruangan belum lengkap:**")
                for r in ruangan_belum:
                    st.write(f"- {r}")

            with col2:
                st.write("")
                st.write("")
                if st.button("Kirim Email", key=f"kurang_{nomor}"):
                    sukses = kirim_email(
                        row["Email Petugas"],
                        nama,
                        "TIDAK_LENGKAP",
                        row["Tanggal"]
                    )
                    st.success("Email terkirim") if sukses else st.error("Gagal kirim email")

        nomor += 1

    if nomor == 1:
        st.success("🎉 Semua petugas sudah mengisi dan checklist lengkap!")


# =====================================================
# LOGOUT
# =====================================================
elif menu == "Logout":
    st.session_state.login = False
    st.session_state.menu = "Beranda"
    st.rerun()
