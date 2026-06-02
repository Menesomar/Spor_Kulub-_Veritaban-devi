import streamlit as st
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

# Sayfa Ayarları
st.set_page_config(page_title="Koşu Kulübü Ligi", page_icon="🏃‍♂️", layout="wide")

# Veritabanı Bağlantısı
@st.cache_resource
def init_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT", 3306)
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
        st.rerun() # Sayfayı yenileyerek sistemi aç
    else:
        st.error("E-posta veya şifre hatalı!")

# Çıkış Yapma Fonksiyonu
def logout():
    st.session_state.giris_yapildi = False
    st.session_state.kullanici_id = None
    st.session_state.kullanici_adi = ""
    st.session_state.rol = ""
    st.rerun()

# --- ARAYÜZ (FRONTEND) GÖRÜNÜMÜ ---

if not st.session_state.giris_yapildi:
    # 1. GİRİŞ YAPILMAMIŞSA (LOGIN EKRANI)
    st.title("🏃‍♂️ Koşu Kulübü Sistemine Giriş")
    st.write("Lütfen devam etmek için üye bilgilerinizi girin.")
    
    # Form ile giriş alma
    with st.form("login_form"):
        eposta = st.text_input("E-posta Adresi")
        sifre = st.text_input("Şifre", type="password")
        submit_button = st.form_submit_button("Sisteme Giriş Yap")
        
        if submit_button:
            login(eposta, sifre)

else:
    # 2. GİRİŞ YAPILMIŞSA (ANA SİSTEM)
    st.sidebar.title(f"Hoş geldin, {st.session_state.kullanici_adi} 👋")
    st.sidebar.success(f"Yetki Seviyesi: **{st.session_state.rol}**")
    
    # Kullanıcının yetkisine göre menü seçenekleri
    if st.session_state.rol == "Admin":
        menu = ["🏆 Liderlik Tablosu", "➕ Yeni Koşu Ekle", "📈 Genel Analiz"]
    else:
        menu = ["🏆 Liderlik Tablosu", "👤 Kendi Profilim"]
        
    secim = st.sidebar.radio("Sayfalar", menu)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Çıkış Yap 🚪"):
        logout()

    # Sayfa Yönlendirmeleri
    if secim == "🏆 Liderlik Tablosu":
        st.header("🏆 Güncel Liderlik Tablosu")
        st.info("Buraya veritabanından çektiğimiz sıralama tablosu eklenecek.")
        
    elif secim == "➕ Yeni Koşu Ekle":
        st.header("➕ Sisteme Yeni Koşu Verisi Gir")
        st.info("Buraya veritabanına INSERT yapacak Admin formu gelecek.")
        
    elif secim == "📈 Genel Analiz":
        st.header("📈 Kulüp Genel Analizi")
        st.info("Buraya kulübün grafiksel (pasta/çizgi) istatistikleri gelecek.")
        
    elif secim == "👤 Kendi Profilim":
        st.header("👤 Profilim ve Koşu Geçmişim")
        st.info(f"Burada sadece {st.session_state.kullanici_adi} adlı kullanıcının geçmişi listelenecek.")