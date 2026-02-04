import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import hashlib
import base64
import re

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Monitoring Kebersihan BPS Kota Cilegon",
    layout="wide"
)

# =====================================================
# LOAD IMAGE BASE64 (LOGO & BACKGROUND)
# =====================================================
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

LOGO_BPS = get_base64("logo_bps.png")
BG_CLEAN = get_base64("bg2.png")

def header_bps():
    st.markdown(f"""
    <div style="
        display:flex;
        align-items:center;
        gap:15px;
        margin-bottom:25px;
    ">
        <img src="data:image/png;base64,{LOGO_BPS}" width="70">
        <div style="
            font-size:22px;
            font-weight:700;
            color:#0B3C5D;
        ">
            Badan Pusat Statistik Kota Cilegon
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# GLOBAL STYLE
# =====================================================
st.markdown(f"""
<style>

/* ================= FONT ================= */
html, body, [class*="css"] {{
    font-family: "Times New Roman", Times, serif;
}}

/* ================= BACKGROUND ================= */
[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)),
        url("data:image/png;base64,{BG_CLEAN}");
    background-size: cover;
    background-position: center;
}}

/* ================= SIDEBAR ================= */
[data-testid="stSidebar"] {{
    background-color: #0B3C5D;
    padding-top: 20px;
}}

/* WRAPPER MENU */
.menu-wrapper {{
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 10px;
}}

/* BUTTON MENU */
[data-testid="stSidebar"] button {{
    background-color: #0E4A73 !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 12px !important;
    border: none !important;
}}

/* HOVER */
[data-testid="stSidebar"] button:hover {{
    background-color: #1C6EA4 !important;
    color: white !important;
}}

/* BUTTON AKTIF (BERDASARKAN MENU) */
[data-testid="stSidebar"] button:has(span:contains("Beranda")) {{
    box-shadow: none;
}}

/* HILANGKAN FOCUS RING */
[data-testid="stSidebar"] button:focus {{
    outline: none !important;
    box-shadow: none !important;
}}

/* TEKS BUTTON */
[data-testid="stSidebar"] button span {{
    color: white !important;
    font-size: 15px;
}}

/* ================= KONTEN UTAMA ================= */
/* HANYA TEKS, BUKAN GAMBAR */
section.main p,
section.main span,
section.main label,
section.main div,
section.main h1,
section.main h2,
section.main h3,
section.main h4 {{
    color: black !important;
}}

/* ================= LOGIN INPUT ================= */
section.main input {{
    background-color: white !important;
    color: black !important;
    border-radius: 6px;
    border: 1px solid #999;
}}

section.main input::placeholder {{
    color: #666 !important;
}}

/* ================= DATAFRAME ================= */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] table {{
    background-color: white !important;
}}

[data-testid="stDataFrame"] th {{
    background-color: white !important;
    color: black !important;
    font-weight: 800 !important;
}}

[data-testid="stDataFrame"] td {{
    background-color: white !important;
    color: black !important;
    font-weight: 600 !important;
}}

/* ================= HEADER ================= */
.header {{
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 10px 0px 20px 0px;
}}

.header img {{
    width: 55px;
    opacity: 1;
}}

.header-title {{
    font-size: 20px;
    font-weight: 700;
    color: #0B3C5D;
}}

</style>
""", unsafe_allow_html=True)

# =====================================================
# EMAIL CONFIG
# =====================================================
EMAIL_PENGIRIM = "jovitacw13@gmail.com"
EMAIL_PASSWORD = "hvrqmxxxxscajxbn"

def kirim_email(tujuan, nama_petugas, status, tanggal, detail=""):
    if status == "BELUM":
        subject = f"⚠️ Peringatan Belum Mengisi Google Form – {nama_petugas}"
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
checklist yang BELUM lengkap:

{detail}

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
# 🔐 TAMBAHAN: MULTI ADMIN (EMAIL SAJA DI KODE)
# =====================================================
ADMINS = [
    "fidelaadn06@gmail.com",
    "admin2@bps.go.id",
]

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# =====================================================
# MASTER ZONA & PETUGAS
# =====================================================
PETUGAS_ZONA = {
    "Petugas Jaga": "Zona 1",
    "Salmin": "Zona 2",
    "Rudi": "Zona 3"
}

# =====================================================
# DETAIL PEKERJAAN
# =====================================================
PEKERJAAN = {
    "Zona 1": {
        "Ruang Rapat Kecil": [
            "Tirai dibuka sebelum mulai kerja dan ditutup kembali setelah jam kerja selesai",
            "Kebersihan lantai",
            "Kebersihan dan kerapihan meja kursi",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Ruang Resepsionis dan Pintu Masuk": [
            "Kebersihan lantai",
            "Kebersihan dan kerapihan meja resepsionis",
            "Kebersihan dinding kaca",
            "Kebersihan dan kerapihan meja kursi",
            "Pengharum ruangan tidak dalam kondisi kosong",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Ruang PST": [
            "Tirai dibuka sebelum mulai kerja dan ditutup kembali setelah jam kerja selesai",
            "Kebersihan lantai",
            "Kebersihan dan kerapihan meja kursi",
            "Kebersihan dinding kaca",
            "PC, monitor dan printer kondisi mati saat jam kerja selesai",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Halaman Depan": [
            "Kebersihan halaman depan",
            "Menyiram tanaman",
            "Rumput berada dalam kondisi rapi dan terawat."
        ]
    },
    "Zona 2": {
        "Ruang Laktasi": [
            "Kebersihan lantai",
            "Kebersihan dan kerapihan meja kursi",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Toilet Pengunjung": [
            "Kebersihan toilet",
            "Memastikan kran air tertutup",
            "Ketersediaan tisu",
            "Tong sampah tidak dalam kondisi penuh",
            "Kebersihan Cermin",
            "Kebersihan Wastafel",
            "Hand soap tidak dalam kondisi kosong",
            "Pengharum ruangan tidak dalam kondisi kosong",
            "Keset di toilet tetap bersih, kering, dan tertata rapi.",
            "Penggantian keset dilakukan secara berkala dan sesuai kondisi.",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Ruang Harmoni (Rapat Besar)": [
            "Tirai dibuka sebelum mulai kerja dan ditutup kembali setelah jam kerja selesai",
            "Kebersihan lantai",
            "Kebersihan dan kerapihan meja kursi, dan peralatan lain",
            "Kebersihan dinding kaca",
            "Tong sampah tidak dalam kondisi penuh",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Ruang Tata Usaha": [
            "Tirai dibuka sebelum mulai kerja dan ditutup kembali setelah jam kerja selesai",
            "Kebersihan lantai",
            "Kebersihan dan kerapihan meja kursi, dan peralatan lain",
            "Kebersihan dinding kaca",
            "Tong sampah tidak dalam kondisi penuh",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Halaman Belakang": [
            "Kebersihan halaman belakang",
            "Menyiram tanaman",
            "Rumput berada dalam kondisi rapi dan terawat"
        ]
    },
    "Zona 3": {
        "Ruang Pengolahan": [
            "Kebersihan lantai",
            "Kebersihan dan kerapihan meja kursi",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Ruang Pantri & Toilet pegawai": [
            "Kebersihan toilet",
            "Memastikan kran air tertutup",
            "Ketersediaan tisu",
            "Tong sampah tidak dalam kondisi penuh",
            "Kebersihan lantai, meja dan kursi pantri",
            "Kebersihan Cermin",
            "Kebersihan Wastafel",
            "Hand soap tidak dalam kondisi kosong",
            "Pengharum ruangan tidak dalam kondisi kosong",
            "Cup lampu pantri dalam kondisi bersih",
            "Keset di toilet tetap bersih, kering, dan tertata rapi",
            "Penggantian keset dilakukan secara berkala dan sesuai kondisi",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Ruang Dinamis (flexible area)": [
            "Tirai dibuka sebelum mulai kerja dan ditutup kembali setelah jam kerja selesai",
            "Kebersihan lantai",
            "Kebersihan dan kerapihan meja kursi, dan peralatan lain",
            "Kebersihan dinding kaca",
            "Tong sampah tidak dalam kondisi penuh",
            "Membersihkan peralatan komputer",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Ruang Mushola": [
            "Kebersihan Karpet dan lantai",
            "Kebersihan rak sepatu dan lantai",
            "AC mati setelah jam kerja",
            "Kebersihan tempat wudhu",
            "Keset di toilet tetap bersih, kering, dan tertata rapi",
            "Penggantian keset dilakukan secara berkala dan sesuai kondisi",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Ruang Arsip": [
            "Kebersihan lantai",
            "AC mati setelah jam kerja",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Ruang Gudang": [
            "Kerapihan area gudang",
            "Membersihkan sudut-sudut plafon ruangan dari sawangan"
        ],
        "Halaman Samping": [
            "Kebersihan halaman samping",
            "Menyiram tanaman",
            "Memastikan rumput berada dalam kondisi rapi dan terawat"
        ]
    }
}

# =====================================================
# LOAD DATA
# =====================================================
data = pd.read_csv("form.csv")
data["Tanggal"] = pd.to_datetime(
    data["Tanggal Pelaksanaan  "],
    dayfirst=True,
    errors="coerce"
).dt.date

hari_ini = datetime.now().date()

# =====================================================
# PARSE JAWABAN GFORM
# =====================================================
def normalize_text(text):
    return re.sub(r"[^\w\s]", "", text.lower()).strip()

def parse_jawaban(value):
    if pd.isna(value) or value == "":
        return []
    return [normalize_text(x) for x in str(value).split(",")]

def cek_detail_kurang(row, zona):
    hasil = {}

    for ruangan, items_wajib in PEKERJAAN[zona].items():
        jawaban = parse_jawaban(row.get(ruangan, ""))

        kurang = []
        for item in items_wajib:
            item_norm = normalize_text(item)

            if item_norm not in jawaban:
                kurang.append(item)

        if kurang:
            hasil[ruangan] = kurang

    return hasil

# =====================================================
# STATUS PETUGAS
# =====================================================
def status_petugas(row):
    zona = PETUGAS_ZONA.get(row["Nama Petugas"])
    if not zona:
        return "TIDAK TERDAFTAR"
    return "LENGKAP" if not cek_detail_kurang(row, zona) else "TIDAK LENGKAP"

data["Status Ruangan"] = data.apply(status_petugas, axis=1)

# =====================================================
# PETUGAS HARI INI
# =====================================================
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

    st.markdown(
        "<h2 style='text-align:center;color:black'>Login Admin</h2>",
        unsafe_allow_html=True
    )

    with st.form("login_form"):
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if username in ADMINS:
            st.session_state.login = True
            st.session_state.admin_email = username
            st.success("Login berhasil")
            st.rerun()
        else:
            st.error("Email tidak terdaftar sebagai admin")

    st.stop()

# =====================================================
# MENU
# =====================================================
if "menu" not in st.session_state:
    st.session_state.menu = "Beranda"

st.sidebar.markdown("<div class='menu-wrapper'>", unsafe_allow_html=True)

for m in ["Beranda", "Detail Zona", "Notifikasi", "Logout"]:
    if st.sidebar.button(m, key=f"menu_{m}", use_container_width=True):
        st.session_state.menu = m

st.sidebar.markdown("</div>", unsafe_allow_html=True)

menu = st.session_state.menu

# =====================================================
# BERANDA
# =====================================================
if menu == "Beranda":
    header_bps()
    st.title("Selamat Datang 👋")
    st.subheader("Sistem Monitoring Kebersihan BPS Kota Cilegon")
    st.caption(
        "Sistem ini digunakan untuk memantau kelengkapan checklist kebersihan "
        "berdasarkan pengisian Google Form oleh petugas kebersihan."
    )

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
    header_bps()
    st.subheader("Detail Checklist per Zona")

    zona_pilih = st.selectbox(
        "Pilih Zona",
        list(PEKERJAAN.keys())
    )

    st.caption(
        f"Menampilkan status kelengkapan checklist kebersihan "
        f"berdasarkan hasil pengisian Google Form untuk "
        f"{zona_pilih}."
    )

    rows = []

    for _, row in data.iterrows():
        # hanya tampilkan petugas sesuai zona
        if PETUGAS_ZONA.get(row["Nama Petugas"]) != zona_pilih:
            continue

        detail_kurang = cek_detail_kurang(row, zona_pilih)

        for ruangan in PEKERJAAN[zona_pilih].keys():
            if ruangan in detail_kurang:
                status = "❌ Tidak Lengkap"
            else:
                status = "✅ Lengkap"

            rows.append({
                "Nama Petugas": row["Nama Petugas"],
                "Tanggal": row["Tanggal"],
                "Ruangan": ruangan,
                "Status": status
            })

    if rows:
        df_zona = pd.DataFrame(rows)
        df_zona.insert(0, "No", range(1, len(df_zona) + 1))
        st.dataframe(df_zona, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data untuk zona ini.")

# =====================================================
# NOTIFIKASI
# =====================================================
elif menu == "Notifikasi":
    header_bps()
    st.subheader("Notifikasi")
    st.caption("Email peringatan untuk petugas yang belum mengisi atau checklist belum lengkap")

    nomor = 1

    # =========================================
    # 1. PETUGAS BELUM ISI GFORM
    # =========================================
    st.subheader("❌ Belum Mengisi")

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
                st.error("Status: BELUM")
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
    # 2. PETUGAS CHECKLIST TIDAK LENGKAP
    # =========================================
    st.subheader("⚠️ Checklist Tidak Lengkap")

    for _, row in data_today.iterrows():
        zona = PETUGAS_ZONA.get(row["Nama Petugas"])
        if not zona:
            continue

        detail = cek_detail_kurang(row, zona)
        if detail:
            teks = ""
            for r, i in detail.items():
                teks += f"\n{r}:\n"
                for x in i:
                    teks += f"- {x}\n"

            st.warning(row["Nama Petugas"])
            if st.button(f"Kirim Email {row['Nama Petugas']}"):
                kirim_email(
                    row["Email Petugas"],
                    row["Nama Petugas"],
                    "TIDAK_LENGKAP",
                    row["Tanggal"],
                    teks
                )

        nomor += 1

    if nomor == 1:
        st.success("Semua petugas sudah mengisi dan checklist lengkap!")

# =====================================================
# LOGOUT
# =====================================================
elif menu == "Logout":
    st.session_state.login = False
    st.session_state.menu = "Beranda"
    st.rerun()
