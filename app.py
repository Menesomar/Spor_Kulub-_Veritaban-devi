import streamlit as st
import mysql.connector
import pandas as pd
import os
import datetime
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Run 2 League", page_icon="🏃‍♂️", layout="wide", initial_sidebar_state="expanded")

# --- RUN 2 LEAGUE (SPORTİF & DİNAMİK) CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,900;1,800;1,900&family=Roboto+Mono:wght@700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        color: #111111;
    }
    
    .stApp {
        background-color: #F4F6F8;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* --- YAN MENÜ --- */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #E5E7EB !important;
        box-shadow: 5px 0 15px rgba(0,0,0,0.02);
    }
    
    div[role="radiogroup"] > label {
        background-color: #F9FAFB !important;
        border-radius: 4px !important;
        padding: 14px 16px !important;
        margin-bottom: 8px !important;
        border: 1px solid #E5E7EB !important;
        transition: all 0.2s ease;
    }
    
    div[role="radiogroup"] > label:hover {
        background-color: #F3F4F6 !important;
        border-color: #D1D5DB !important;
        transform: translateX(4px);
    }
    
    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #111111 !important;
        border-left: 6px solid #FF4B00 !important;
        border-top: none !important;
        border-bottom: none !important;
        border-right: none !important;
    }
    
    div[role="radiogroup"] > label[data-checked="true"] p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* --- BUTONLAR --- */
    .stButton>button {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border: 2px solid #111111 !important;
        border-radius: 4px !important;
        font-weight: 800 !important;
        letter-spacing: 1px;
        padding: 0.8rem 1.5rem !important;
        transition: all 0.2s ease !important;
        width: 100%;
        text-transform: uppercase;
        font-size: 0.9rem !important;
        font-style: italic;
    }
    
    .stButton>button:hover {
        background-color: #FF4B00 !important;
        border-color: #FF4B00 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(255, 75, 0, 0.3) !important;
    }

    /* --- FORMLAR --- */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div {
        border-radius: 4px !important;
        border: 2px solid #E5E7EB !important;
        background-color: #FFFFFF !important;
        color: #111111 !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-baseweb="input"] > div:focus-within, div[data-baseweb="select"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
        border-color: #111111 !important;
        box-shadow: none !important;
    }

    /* --- METRİK KARTLARI --- */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 2px solid #E5E7EB;
        border-left: 6px solid #FF4B00;
        border-radius: 6px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.05);
        border-color: #111111;
    }
    
    div[data-testid="metric-container"] label {
        color: #6B7280 !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    div[data-testid="stMetricValue"] {
        font-family: 'Roboto Mono', monospace !important;
        color: #111111 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -1px;
    }

    /* --- EXPANDER & TABS --- */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        border-radius: 4px !important;
        border: 2px solid #E5E7EB !important;
        font-weight: 800 !important;
        color: #111111 !important;
        transition: all 0.2s ease;
    }
    .streamlit-expanderHeader:hover {
        border-color: #111111 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #E5E7EB;
        border-radius: 4px;
        color: #4B5563;
        font-weight: 700;
        padding: 8px 20px;
        text-transform: uppercase;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #111111 !important;
        color: #FFFFFF !important;
    }
    
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 6px;
        padding: 5px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    hr {
        border-color: #E5E7EB !important;
    }
</style>
""", unsafe_allow_html=True)

# Veritabanı Bağlantısı
@st.cache_resource
def init_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT", 3306),
            autocommit=True
        )
    except Exception as e:
        st.error(f"Veritabanı Bağlantı Hatası: {e}")
        return None

conn = init_connection()

# Oturum Ayarları
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_id = None
    st.session_state.kullanici_adi = ""
    st.session_state.rol = ""

def login(eposta, sifre):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT Uye_ID, Ad, Soyad, Rol FROM Uyeler WHERE Eposta = %s AND Sifre = %s", (eposta, sifre))
    user = cursor.fetchone()
    cursor.close()
    
    if user:
        st.session_state.giris_yapildi = True
        st.session_state.kullanici_id = user['Uye_ID']
        st.session_state.kullanici_adi = f"{user['Ad']} {user['Soyad']}"
        st.session_state.rol = user['Rol']
        st.rerun()
    else:
        st.error("E-posta veya şifre hatalı!")

def logout():
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_id = None
    st.session_state.kullanici_adi = ""
    st.session_state.rol = ""
    st.rerun()

# ==========================================
# --- ARAYÜZ (FRONTEND) GÖRÜNÜMÜ ---
# ==========================================

if not st.session_state.giris_yapildi:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # --- RUN 2 LEAGUE MARKA KİMLİĞİ ---
        st.markdown("""
        <div style='background-color: #FFFFFF; padding: 40px 30px; border-radius: 8px; border: 2px solid #E5E7EB; border-top: 8px solid #FF4B00; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center;'>
            <h1 style='color: #111111; font-weight: 900; font-style: italic; letter-spacing: -2px; text-transform: uppercase; margin-bottom: 5px; font-size: 3.5rem;'>RUN <span style='color: #FF4B00;'>2</span> LEAGUE</h1>
            <h4 style='color: #6B7280; font-weight: 700; letter-spacing: 4px; margin-top: 0px; margin-bottom: 25px; text-transform: uppercase; font-size: 0.9rem;'>Performans & Lig Sistemi</h4>
            <p style='color: #4B5563; font-size: 1rem; font-weight: 500;'>Antrenmanlara başlamak için sisteme giriş yapın.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Yeni Kayıt Oluştur"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                eposta = st.text_input("E-posta Adresi")
                sifre = st.text_input("Şifre", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("SİSTEME GİRİŞ YAP"):
                    login(eposta, sifre)
                    
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("kayit_form"):
                k_col1, k_col2 = st.columns(2)
                yeni_ad = k_col1.text_input("Ad")
                yeni_soyad = k_col2.text_input("Soyad")
                
                yeni_eposta = st.text_input("E-posta Adresi")
                yeni_cinsiyet = st.selectbox("Cinsiyet", ["Erkek (E)", "Kadın (K)"])
                
                s_col1, s_col2 = st.columns(2)
                yeni_sifre = s_col1.text_input("Şifre", type="password")
                yeni_sifre_tekrar = s_col2.text_input("Şifre (Tekrar)", type="password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("KAYIT OL VE BAŞLA 🚀"):
                    if yeni_sifre != yeni_sifre_tekrar:
                        st.error("Şifreler eşleşmiyor! Lütfen kontrol edin.")
                    elif not yeni_ad or not yeni_soyad or not yeni_eposta or not yeni_sifre:
                        st.error("Lütfen tüm alanları doldurun.")
                    else:
                        cinsiyet_kodu = "E" if "Erkek" in yeni_cinsiyet else "K"
                        try:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO Uyeler (Ad, Soyad, Eposta, Cinsiyet, Sifre) VALUES (%s, %s, %s, %s, %s)", (yeni_ad, yeni_soyad, yeni_eposta, cinsiyet_kodu, yeni_sifre))
                            yeni_uye_id = cursor.lastrowid
                            mevcut_yil = datetime.datetime.now().year
                            cursor.execute("INSERT INTO Uye_Sezon_Lig (Uye_ID, Lig_ID, Sezon_Yili, ToplamPuan) VALUES (%s, %s, %s, %s)", (yeni_uye_id, 1, mevcut_yil, 0))
                            conn.commit()
                            cursor.close()
                            st.success("🎉 Kayıt başarıyla oluşturuldu! Şimdi 'Giriş Yap' sekmesinden sisteme girebilirsiniz.")
                        except mysql.connector.IntegrityError:
                            st.error("Bu e-posta adresi zaten kullanımda!")
                        except Exception as e:
                            st.error(f"Kayıt hatası: {e}")

else:
    # --- YAN MENÜ MARKA ALANI ---
    st.sidebar.markdown("<h2 style='color: #111111; font-weight: 900; font-style: italic; letter-spacing: -1px; text-align: center; margin-bottom: 0;'>RUN <span style='color: #FF4B00;'>2</span> LEAGUE</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='border-color: #E5E7EB; margin: 10px 0 20px 0;'>", unsafe_allow_html=True)
    
    st.sidebar.markdown(f"<h4 style='color: #111111; font-weight: 800; margin-bottom: 0; text-transform: uppercase;'>{st.session_state.kullanici_adi}</h4>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='color: #FF4B00; font-weight: 800; font-size: 0.85rem; letter-spacing: 1px;'>{st.session_state.rol.upper()}</p>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.caption("SEZON İLERLEMESİ")
    st.sidebar.progress(85, text="Aktiflik (%85)")
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.rol == "Admin":
        menu = ["📢 Duyurular", "🏆 Liderlik Tablosu", "➕ Yeni Koşu Ekle (Admin)", "⚖️ Ceza & Lig Düşürme", "✍️ Duyuru Yayınla", "👥 Tüm Üyeler", "👤 Kendi Profilim"]
    else:
        menu = ["📢 Duyurular", "🏆 Liderlik Tablosu", "🏃‍♂️ Koşumu Kaydet", "👤 Kendi Profilim"]
        
    secim = st.sidebar.radio("Sistem Menüsü", menu, label_visibility="collapsed")
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 SİSTEMDEN ÇIKIŞ"):
        logout()

    if secim == "📢 Duyurular":
        st.markdown("<h1 style='color: #111111; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -1px;'>📢 Sistem Panosu</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4B5563; font-weight: 500;'>Run 2 League genelindeki en son gelişmeler ve antrenman bildirimleri.</p><hr>", unsafe_allow_html=True)
        
        dash_col1, dash_col2, dash_col3 = st.columns(3)
        with dash_col1:
            st.info("🏃‍♂️ LİG HEDEFİ: 10.000 KM")
        with dash_col2:
            st.success("🟢 SUNUCU: ÇEVRİMİÇİ")
        with dash_col3:
            st.warning("⚡ SON GÜNCELLEME: BUGÜN")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        try:
            query = "SELECT D.Baslik, D.Icerik, D.Tarih, U.Ad, U.Soyad FROM Duyurular D LEFT JOIN Uyeler U ON D.Yazar_ID = U.Uye_ID ORDER BY D.Tarih DESC"
            df_duyuru = pd.read_sql(query, conn)
            
            if not df_duyuru.empty:
                for index, row in df_duyuru.iterrows():
                    with st.expander(f"📌 {row['Baslik']} - ({row['Tarih'].strftime('%d.%m.%Y %H:%M')})", expanded=True):
                        st.markdown(f"<p style='color: #374151; font-size: 1.05rem; font-weight: 500;'>{row['Icerik']}</p>", unsafe_allow_html=True)
                        st.caption(f"Yayınlayan: {row['Ad']} {row['Soyad']}")
            else:
                st.info("Henüz panoda bir duyuru bulunmuyor.")
        except Exception as e: pass

    elif secim == "✍️ Duyuru Yayınla":
        st.markdown("<h1 style='color: #111111; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -1px;'>✍️ Yeni Duyuru Yayınla</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4B5563; font-weight: 500;'>Run 2 League üyelerinin görebileceği yeni bir bildirim oluşturun.</p><hr>", unsafe_allow_html=True)
        
        with st.form("duyuru_form", clear_on_submit=True):
            baslik = st.text_input("Duyuru Başlığı")
            icerik = st.text_area("Duyuru İçeriği", height=150)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("PANODA YAYINLA 📣"):
                if baslik and icerik:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Duyurular (Baslik, Icerik, Yazar_ID) VALUES (%s, %s, %s)", (baslik, icerik, st.session_state.kullanici_id))
                        conn.commit()
                        st.success("Duyuru başarıyla yayınlandı!")
                    except Exception as e: pass
                else:
                    st.error("Lütfen başlık ve içerik alanlarını boş bırakmayın.")

    elif secim == "🏆 Liderlik Tablosu":
        st.markdown("<h1 style='color: #111111; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -1px;'>🏆 Liderlik Tablosu</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4B5563; font-weight: 500;'>Liglere göre güncel performans durumu ve puan sıralamaları.</p><hr>", unsafe_allow_html=True)
        try:
            query = "SELECT * FROM VW_CanliLigSiralama"
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                aktif_ligler = df['LigAdi'].unique().tolist()
                sekmeler = st.tabs([f"🏅 {lig}" for lig in aktif_ligler])
                for sekme, lig_adi in zip(sekmeler, aktif_ligler):
                    with sekme:
                        st.markdown("<br>", unsafe_allow_html=True)
                        lig_verisi = df[df['LigAdi'] == lig_adi].drop(columns=['LigAdi'])
                        st.dataframe(lig_verisi, use_container_width=True, hide_index=True)
        except Exception as e: pass

    elif secim == "🏃‍♂️ Koşumu Kaydet":
        st.markdown("<h1 style='color: #111111; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -1px;'>🏃‍♂️ Antrenman Kaydı</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4B5563; font-weight: 500;'>Bugün tamamladığın rotayı gir. Performans değerlerin otomatik işlenecektir.</p><hr>", unsafe_allow_html=True)
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Rota_ID, RotaAdi, ZorlukKatsayisi FROM Rotalar") 
            rotalar = cursor.fetchall()
            rota_sozlugu = {f"{r['RotaAdi']} (Zorluk: {r['ZorlukKatsayisi']})": r['Rota_ID'] for r in rotalar}

            with st.form("kendi_kosumu_ekle_form", clear_on_submit=True):
                secilen_rota = st.selectbox("Koştuğun Rota", list(rota_sozlugu.keys()))
                
                col1, col2 = st.columns(2)
                mesafe_km = col1.number_input("Koşulan Mesafe (KM)", min_value=0.1, step=0.1, format="%.1f")
                sure_dk = col2.number_input("Toplam Süre (Dakika)", min_value=1, step=1)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("PERFORMANSI GÖNDER 🚀"):
                    try:
                        cursor = conn.cursor()
                        cursor.callproc('SP_YeniKosuEkle', (st.session_state.kullanici_id, rota_sozlugu[secilen_rota], mesafe_km, sure_dk))
                        st.success("🎉 Harika iş! Antrenmanın başarıyla kaydedildi.")
                    except mysql.connector.Error as err:
                        st.error(f"Kayıt Reddedildi: {err.msg}")
        except Exception as e: pass

    elif secim == "➕ Yeni Koşu Ekle (Admin)":
        st.markdown("<h1 style='color: #111111; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -1px;'>➕ Veri Girişi</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4B5563; font-weight: 500;'>Sisteme manuel koşu verisi girişi (Hakem Ekranı).</p><hr>", unsafe_allow_html=True)
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Rota_ID, RotaAdi, ZorlukKatsayisi FROM Rotalar") 
            rota_sozlugu = {f"{r['RotaAdi']} (Zorluk: {r['ZorlukKatsayisi']})": r['Rota_ID'] for r in cursor.fetchall()}
            
            cursor.execute("SELECT Uye_ID, Ad, Soyad FROM Uyeler")
            uye_sozlugu = {f"{u['Ad']} {u['Soyad']} (ID: {u['Uye_ID']})": u['Uye_ID'] for u in cursor.fetchall()}

            with st.form("kosu_ekle_form", clear_on_submit=True):
                secilen_uye = st.selectbox("Koşuyu Yapan Üye", list(uye_sozlugu.keys()))
                secilen_rota = st.selectbox("Koşulan Rota", list(rota_sozlugu.keys()))
                col1, col2 = st.columns(2)
                mesafe_km = col1.number_input("Mesafe (KM)", min_value=0.1, step=0.1, format="%.1f")
                sure_dk = col2.number_input("Koşu Süresi (Dakika)", min_value=1, step=1)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("VERİYİ İŞLE ⏱️"):
                    try:
                        cursor = conn.cursor()
                        cursor.callproc('SP_YeniKosuEkle', (uye_sozlugu[secilen_uye], rota_sozlugu[secilen_rota], mesafe_km, sure_dk))
                        st.success("🎉 Koşu eklendi! Lig durumu otomatik hesaplandı.")
                    except mysql.connector.Error as err:
                        st.error(f"Kayıt Reddedildi: {err.msg}")
        except Exception as e: pass

    elif secim == "⚖️ Ceza & Lig Düşürme":
        st.markdown("<h1 style='color: #111111; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -1px;'>⚖️ Disiplin Kurulu</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4B5563; font-weight: 500;'>Üyelerden puan silin ve lig düşürme işlemlerini yönetin.</p><hr>", unsafe_allow_html=True)
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT U.Uye_ID, U.Ad, U.Soyad, USL.ToplamPuan, L.LigAdi FROM Uyeler U JOIN Uye_Sezon_Lig USL ON U.Uye_ID = USL.Uye_ID JOIN Ligler L ON USL.Lig_ID = L.Lig_ID")
            uye_sozlugu = {f"{u['Ad']} {u['Soyad']} - {u['LigAdi']} ({u['ToplamPuan']} Puan)": u['Uye_ID'] for u in cursor.fetchall()}
            
            with st.form("ceza_form"):
                secilen_uye = st.selectbox("İşlem Yapılacak Üye", list(uye_sozlugu.keys()))
                ceza_puani = st.number_input("Silinecek Puan Miktarı", min_value=1, step=50)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("CEZAYI UYGULA 📉"):
                    try:
                        cursor = conn.cursor()
                        cursor.callproc('SP_CezaPuaniVer', (uye_sozlugu[secilen_uye], ceza_puani))
                        st.success(f"Cezai işlem uygulandı! Kullanıcının güncel durumu hesaplandı.")
                    except Exception as e: pass
        except Exception as e: pass

    elif secim == "👥 Tüm Üyeler":
        st.markdown("<h1 style='color: #111111; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -1px;'>👥 Run 2 League Sicili</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4B5563; font-weight: 500;'>Sisteme kayıtlı tüm kullanıcıların detaylı listesi.</p><hr>", unsafe_allow_html=True)
        try:
            df_uyeler = pd.read_sql("SELECT Uye_ID as ID, Ad, Soyad, Eposta, Rol, Cinsiyet, DATE_FORMAT(KayitTarihi, '%d.%m.%Y') as 'Kayıt Tarihi' FROM Uyeler ORDER BY Uye_ID DESC", conn)
            st.dataframe(df_uyeler, use_container_width=True, hide_index=True)
        except Exception as e: pass

    elif secim == "👤 Kendi Profilim":
        st.markdown(f"<h1 style='color: #111111; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -1px;'>👤 Sporcu Profili</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #4B5563; font-weight: 500;'>Kişisel antrenman geçmişin ve güncel performans değerlerin.</p><hr>", unsafe_allow_html=True)
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT L.LigAdi, USL.ToplamPuan FROM Uye_Sezon_Lig USL JOIN Ligler L ON USL.Lig_ID = L.Lig_ID WHERE USL.Uye_ID = %s AND USL.Sezon_Yili = %s", (st.session_state.kullanici_id, datetime.datetime.now().year))
            lig_durumu = cursor.fetchone()
            
            if lig_durumu:
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric("GÜNCEL LİGİNİZ", f"{lig_durumu['LigAdi']}")
                with m_col2:
                    st.metric("GENEL PUAN", f"{lig_durumu['ToplamPuan']}")
                with m_col3:
                    st.metric("AKTİF SEZON", str(datetime.datetime.now().year))
            
            st.markdown("<br><h3 style='color: #111111; font-weight: 800; font-style: italic; text-transform: uppercase;'>Son Antrenmanlar</h3>", unsafe_allow_html=True)
            query = f"SELECT R.RotaAdi as 'Rota', DATE_FORMAT(K.KosuTarihi, '%d.%m.%Y') as 'Tarih', K.Mesafe_KM as 'Mesafe (KM)', K.Sure_Dakika as 'Süre (Dk)', K.KazanilanPuan as 'Kazanılan Puan' FROM Kosular K JOIN Rotalar R ON K.Rota_ID = R.Rota_ID WHERE K.Uye_ID = {st.session_state.kullanici_id} ORDER BY K.KosuTarihi DESC"
            df_gecmis = pd.read_sql(query, conn)
            
            if not df_gecmis.empty:
                st.dataframe(df_gecmis, use_container_width=True, hide_index=True)
            else:
                st.info("Henüz kaydedilmiş bir antrenmanın bulunmuyor.")
        except Exception as e: pass