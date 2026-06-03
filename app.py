import streamlit as st
import mysql.connector
import pandas as pd
import os
import datetime
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Koşu Kulübü Ligi", page_icon="🏃‍♂️", layout="wide", initial_sidebar_state="expanded")

# --- PREMIUM GLASSMORPHISM & ANİMASYON CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1E293B;
    }
    
    /* Arka planı çok hafif bir degrade yaparak cam efektinin parlamasını sağla */
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* --- SAYFA YÜKLENME ANİMASYONU --- */
    @keyframes fadeUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .main .block-container {
        animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* --- YAN MENÜ (GLASSMORPHISM / CAM EFEKTİ) --- */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.6) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.02);
    }
    
    div[role="radiogroup"] > label {
        background-color: transparent !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        margin-bottom: 8px !important;
        border: 1px solid transparent !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 1) !important;
        transform: translateX(6px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
    div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFFFFF 100%) !important;
        border-left: 5px solid #C19A6B !important;
        border-top: 1px solid rgba(255,255,255,0.8) !important;
        border-bottom: 1px solid rgba(255,255,255,0.8) !important;
        border-right: 1px solid rgba(255,255,255,0.8) !important;
        border-radius: 0 12px 12px 0 !important;
        box-shadow: 0 4px 15px rgba(193, 154, 107, 0.08) !important;
    }

    /* --- PREMIUM BUTONLAR (DİNAMİK GÖLGE VE IŞIMA) --- */
    .stButton>button {
        background: linear-gradient(135deg, #C19A6B 0%, #A67C52 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        padding: 0.7rem 1.5rem !important;
        box-shadow: 0 6px 16px rgba(193, 154, 107, 0.25), inset 0 2px 4px rgba(255,255,255,0.1) !important;
        transition: all 0.3s ease !important;
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(193, 154, 107, 0.4), inset 0 2px 4px rgba(255,255,255,0.2) !important;
    }

    /* --- GİRİŞ ALANLARI --- */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div {
        border-radius: 12px !important;
        border: 1px solid rgba(203, 213, 225, 0.6) !important;
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(8px) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-baseweb="input"] > div:focus-within, div[data-baseweb="select"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
        border-color: #C19A6B !important;
        background: #FFFFFF !important;
        box-shadow: 0 0 0 3px rgba(193, 154, 107, 0.15) !important;
    }

    /* --- METRİK KARTLARI (3D DERİNLİK VE CAM) --- */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.7));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.9);
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04), inset 0 2px 5px rgba(255,255,255,0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border-left: 5px solid #C19A6B;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08), inset 0 2px 5px rgba(255,255,255,0.8);
    }
    
    div[data-testid="metric-container"] label {
        color: #64748B !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1E293B !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #1E293B, #C19A6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* --- DUYURU KARTLARI (EXPANDER) --- */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(8px) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.9) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
        font-weight: 700 !important;
        color: #334155 !important;
        transition: all 0.3s ease;
    }
    .streamlit-expanderHeader:hover {
        background: #FFFFFF !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05) !important;
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

# Oturum (Session) Hafızası Ayarları
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_id = None
    st.session_state.kullanici_adi = ""
    st.session_state.rol = ""

# Giriş Yapma Fonksiyonu
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

# Çıkış Yapma Fonksiyonu
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
        st.markdown("<h1 style='text-align: center; color: #1E293B; font-weight: 800; letter-spacing: -1px;'>🏃‍♂️ Koşu Kulübü Ligi</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 2rem;'>Sisteme giriş yapın veya yeni bir maceraya katılın.</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Yeni Kayıt Oluştur"])
        
        # --- GİRİŞ YAP SEKME ---
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                eposta = st.text_input("E-posta Adresi")
                sifre = st.text_input("Şifre", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Sisteme Giriş Yap"):
                    login(eposta, sifre)
                    
        # --- KAYIT OL SEKME ---
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
                if st.form_submit_button("Kayıt Ol ve Başla 🚀"):
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
    # --- ANA SİSTEM ---
    st.sidebar.markdown(f"<h3 style='color: #1E293B; font-weight: 800;'>Hoş geldin, <br><span style='color: #C19A6B;'>{st.session_state.kullanici_adi}</span> 👋</h3>", unsafe_allow_html=True)
    st.sidebar.caption(f"Yetki Seviyesi: **{st.session_state.rol}**")
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    # MENÜ DÜZENİ
    if st.session_state.rol == "Admin":
        menu = ["📢 Duyurular", "🏆 Liderlik Tablosu", "➕ Yeni Koşu Ekle (Admin)", "⚖️ Ceza & Lig Düşürme", "✍️ Duyuru Yayınla", "👥 Tüm Üyeler", "👤 Kendi Profilim"]
    else:
        menu = ["📢 Duyurular", "🏆 Liderlik Tablosu", "👤 Kendi Profilim"]
        
    secim = st.sidebar.radio("Sistem Menüsü", menu, label_visibility="collapsed")
    
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Sistemden Çıkış Yap"):
        logout()

    st.markdown("<div style='padding-top: 1rem;'></div>", unsafe_allow_html=True)

    # --- 1. DUYURULAR PANOSU ---
    if secim == "📢 Duyurular":
        st.title("📢 Kulüp Panosu")
        st.markdown("<p style='color: #64748B;'>Kulübümüzle ilgili en güncel haberler ve bildirimler.</p><hr style='border-color: rgba(203, 213, 225, 0.4);'>", unsafe_allow_html=True)
        try:
            query = """
                SELECT D.Baslik, D.Icerik, D.Tarih, U.Ad, U.Soyad 
                FROM Duyurular D 
                LEFT JOIN Uyeler U ON D.Yazar_ID = U.Uye_ID 
                ORDER BY D.Tarih DESC
            """
            df_duyuru = pd.read_sql(query, conn)
            
            if not df_duyuru.empty:
                for index, row in df_duyuru.iterrows():
                    with st.expander(f"📌 {row['Baslik']} - ({row['Tarih'].strftime('%d.%m.%Y %H:%M')})", expanded=True):
                        st.write(row['Icerik'])
                        st.caption(f"Yayınlayan: {row['Ad']} {row['Soyad']}")
            else:
                st.info("Henüz panoda bir duyuru bulunmuyor.")
        except Exception as e:
            st.error(f"Duyurular yüklenirken hata oluştu: {e}")

    # --- 2. DUYURU YAYINLA (Sadece Admin) ---
    elif secim == "✍️ Duyuru Yayınla":
        st.title("✍️ Yeni Duyuru Yayınla")
        st.markdown("<p style='color: #64748B;'>Tüm üyelerin görebileceği yeni bir duyuru oluşturun.</p><hr style='border-color: rgba(203, 213, 225, 0.4);'>", unsafe_allow_html=True)
        
        with st.form("duyuru_form", clear_on_submit=True):
            baslik = st.text_input("Duyuru Başlığı")
            icerik = st.text_area("Duyuru İçeriği", height=150)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Panoda Yayınla 📣"):
                if baslik and icerik:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Duyurular (Baslik, Icerik, Yazar_ID) VALUES (%s, %s, %s)", (baslik, icerik, st.session_state.kullanici_id))
                        conn.commit()
                        cursor.close()
                        st.success("Duyuru başarıyla yayınlandı! '📢 Duyurular' sekmesinden kontrol edebilirsiniz.")
                    except Exception as e:
                        st.error(f"Kayıt Hatası: {e}")
                else:
                    st.error("Lütfen başlık ve içerik alanlarını boş bırakmayın.")

    # --- 3. LİDERLİK TABLOSU ---
    elif secim == "🏆 Liderlik Tablosu":
        st.title("🏆 Canlı Liderlik Tablosu")
        st.markdown("<p style='color: #64748B;'>Liglere göre güncel puan durumu ve sıralamalar.</p><hr style='border-color: rgba(203, 213, 225, 0.4);'>", unsafe_allow_html=True)
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
            else:
                st.info("Tabloda veri yok.")
        except Exception as e:
            st.error(f"Tablo çekilirken hata oluştu: {e}")

    # --- 4. YENİ KOŞU EKLE ---
    elif secim == "➕ Yeni Koşu Ekle (Admin)":
        st.title("➕ Yeni Koşu Verisi Gir")
        st.markdown("<p style='color: #64748B;'>Sisteme manuel koşu verisi girişi (Hile koruması aktiftir).</p><hr style='border-color: rgba(203, 213, 225, 0.4);'>", unsafe_allow_html=True)
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Rota_ID, RotaAdi, ZorlukKatsayisi FROM Rotalar") 
            rotalar = cursor.fetchall()
            rota_sozlugu = {f"{r['RotaAdi']} (Zorluk: {r['ZorlukKatsayisi']})": r['Rota_ID'] for r in rotalar}
            
            cursor.execute("SELECT Uye_ID, Ad, Soyad FROM Uyeler")
            uyeler = cursor.fetchall()
            uye_sozlugu = {f"{u['Ad']} {u['Soyad']} (ID: {u['Uye_ID']})": u['Uye_ID'] for u in uyeler}
            cursor.close()

            with st.form("kosu_ekle_form", clear_on_submit=True):
                secilen_uye = st.selectbox("Koşuyu Yapan Üye", list(uye_sozlugu.keys()))
                secilen_rota = st.selectbox("Koşulan Rota", list(rota_sozlugu.keys()))
                
                col1, col2 = st.columns(2)
                mesafe_km = col1.number_input("Mesafe (KM)", min_value=0.1, step=0.1, format="%.1f")
                sure_dk = col2.number_input("Koşu Süresi (Dakika)", min_value=1, step=1)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Koşuyu Kaydet ⏱️"):
                    try:
                        cursor = conn.cursor()
                        cursor.callproc('SP_YeniKosuEkle', (uye_sozlugu[secilen_uye], rota_sozlugu[secilen_rota], mesafe_km, sure_dk))
                        st.success("🎉 Koşu eklendi! Trigger çalıştı, lig durumu güncellendi.")
                    except mysql.connector.Error as err:
                        st.error(f"Kayıt Reddedildi: {err.msg}")
        except Exception as e:
            st.error(f"Hata: {e}")

    # --- 5. CEZA VE LİG DÜŞÜRME ---
    elif secim == "⚖️ Ceza & Lig Düşürme":
        st.title("⚖️ Ceza Puanı Uygula")
        st.markdown("<p style='color: #64748B;'>Üyelerden puan silin ve gerekirse lig düşürme işlemini tetikleyin.</p><hr style='border-color: rgba(203, 213, 225, 0.4);'>", unsafe_allow_html=True)
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT U.Uye_ID, U.Ad, U.Soyad, USL.ToplamPuan, L.LigAdi 
                FROM Uyeler U 
                JOIN Uye_Sezon_Lig USL ON U.Uye_ID = USL.Uye_ID
                JOIN Ligler L ON USL.Lig_ID = L.Lig_ID
            """)
            uyeler = cursor.fetchall()
            uye_sozlugu = {f"{u['Ad']} {u['Soyad']} - {u['LigAdi']} ({u['ToplamPuan']} Puan)": u['Uye_ID'] for u in uyeler}
            cursor.close()
            
            with st.form("ceza_form"):
                secilen_uye = st.selectbox("Ceza Verilecek Üye", list(uye_sozlugu.keys()))
                ceza_puani = st.number_input("Silinecek Puan Miktarı", min_value=1, step=50)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Cezayı Uygula 📉"):
                    uye_id = uye_sozlugu[secilen_uye]
                    try:
                        cursor = conn.cursor()
                        cursor.callproc('SP_CezaPuaniVer', (uye_id, ceza_puani))
                        st.success(f"Cezai işlem uygulandı! Kullanıcının yeni lig durumu hesaplandı.")
                    except Exception as e:
                        st.error(f"İşlem başarısız: {e}")
        except Exception as e:
             st.error(f"Hata: {e}")

    # --- 6. TÜM ÜYELER ---
    elif secim == "👥 Tüm Üyeler":
        st.title("👥 Kulüp Üyeleri Yönetimi")
        st.markdown("<p style='color: #64748B;'>Sisteme kayıtlı tüm kullanıcıların listesi.</p><hr style='border-color: rgba(203, 213, 225, 0.4);'>", unsafe_allow_html=True)
        try:
            df_uyeler = pd.read_sql("SELECT Uye_ID as ID, Ad, Soyad, Eposta, Rol, Cinsiyet, DATE_FORMAT(KayitTarihi, '%d.%m.%Y') as 'Kayıt Tarihi' FROM Uyeler ORDER BY Uye_ID DESC", conn)
            st.dataframe(df_uyeler, use_container_width=True, hide_index=True)
        except Exception as e: pass

    # --- 7. KENDİ PROFİLİM ---
    elif secim == "👤 Kendi Profilim":
        st.title("👤 Profilim")
        st.markdown("<p style='color: #64748B;'>Kişisel koşu geçmişiniz ve güncel istatistikleriniz.</p><hr style='border-color: rgba(203, 213, 225, 0.4);'>", unsafe_allow_html=True)
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT L.LigAdi, USL.ToplamPuan FROM Uye_Sezon_Lig USL JOIN Ligler L ON USL.Lig_ID = L.Lig_ID WHERE USL.Uye_ID = %s AND USL.Sezon_Yili = %s", (st.session_state.kullanici_id, datetime.datetime.now().year))
            lig_durumu = cursor.fetchone()
            
            if lig_durumu:
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    st.metric("Güncel Liginiz", f"🏅 {lig_durumu['LigAdi']}")
                with m_col2:
                    st.metric("Toplam Puanınız", f"⭐ {lig_durumu['ToplamPuan']}")
            
            st.markdown("<br><h4 style='color: #1E293B; font-weight: 700;'>Son Koşularınız</h4>", unsafe_allow_html=True)
            query = f"SELECT R.RotaAdi as 'Rota', DATE_FORMAT(K.KosuTarihi, '%d.%m.%Y') as 'Tarih', K.Mesafe_KM as 'Mesafe (KM)', K.Sure_Dakika as 'Süre (Dk)', K.KazanilanPuan as 'Kazanılan Puan' FROM Kosular K JOIN Rotalar R ON K.Rota_ID = R.Rota_ID WHERE K.Uye_ID = {st.session_state.kullanici_id} ORDER BY K.KosuTarihi DESC"
            df_gecmis = pd.read_sql(query, conn)
            
            if not df_gecmis.empty:
                st.dataframe(df_gecmis, use_container_width=True, hide_index=True)
            else:
                st.info("Henüz kaydedilmiş bir koşunuz bulunmuyor.")
        except Exception as e: pass