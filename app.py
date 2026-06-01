import streamlit as st
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

# 1. Adımda oluşturduğumuz .env dosyasındaki şifreleri gizlice içeri alıyoruz
load_dotenv()

# --- SİTE AYARLARI ---
st.set_page_config(page_title="Koşu Kulübü Ligi", page_icon="🏃", layout="wide")

# Siteye biraz renk ve tasarım katıyoruz
st.markdown("""
    <style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- VERİTABANINA BAĞLANMA KISMI ---
# Site her yenilendiğinde çökmek yerine bağlantıyı hafızada tutsun diye @st.cache_resource kullanıyoruz
@st.cache_resource
def init_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT", 3306) # Mac MAMP kapısı için eklendi
        )
    except Exception as e:
        st.error(f"Veritabanı Bağlantı Hatası: {e}")
        return None

# Bağlantıyı çalıştır
conn = init_connection()

# Eğer veritabanı (MAMP/XAMPP) kapalıysa siteyi durdur ve uyarı ver
if conn is None:
    st.warning("Lütfen yerel MySQL sunucunuzun açık olduğundan emin olun.")
    st.stop()

# Verileri çekmek için bir okuyucu (cursor) oluştur
cursor = conn.cursor(dictionary=True)

# --- SOL TARAFTAKİ MENÜ ---
st.sidebar.title("🏃 Koşu Kulübü")
menu = st.sidebar.radio("Menü Seçin", ["🏆 Liderlik Tablosu", "🗺️ Rota İstatistikleri"])
st.sidebar.markdown("---")
st.sidebar.caption("Veritabanı Yönetim Sistemleri Projesi")

# --- SAYFA 1: LİDERLİK TABLOSU ---
if menu == "🏆 Liderlik Tablosu":
    st.header("Güncel Lig Sıralaması")

    # SQL'deki görünümü (View) çalıştırıp verileri alıyoruz
    cursor.execute("SELECT * FROM VW_CanliLigSiralama")
    lig_verisi = cursor.fetchall()

    # Eğer içeride veri varsa tabloyu çiz
    if lig_verisi:
        df_lig = pd.DataFrame(lig_verisi)
        
        # En üstte yan yana 3 tane istatistik kutusu oluşturuyoruz
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Üye", len(df_lig))
        col2.metric("En Yüksek Puan", df_lig['ToplamPuan'].max())
        col3.metric("Toplam Mesafe", f"{df_lig['ToplamKosulan_KM'].sum()} KM")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Sütun isimlerini Türkçeleştirip daha güzel gösteriyoruz
        df_lig.rename(columns={
            'Ad': 'İsim', 'Soyad': 'Soyisim', 'LigAdi': 'Lig', 
            'ToplamPuan': 'Puan', 'ToplamKosulan_KM': 'Koşulan Mesafe (KM)'
        }, inplace=True)
        
        # Tabloyu ekrana basıyoruz
        st.dataframe(df_lig[['İsim', 'Soyisim', 'Lig', 'Puan', 'Koşulan Mesafe (KM)']], use_container_width=True, hide_index=True)
    else:
        st.info("Kayıtlı koşu verisi bulunamadı.")

# --- SAYFA 2: ROTA İSTATİSTİKLERİ ---
elif menu == "🗺️ Rota İstatistikleri":
    st.header("Rota Tercihleri ve Zorluklar")

    # İkinci SQL görünümünü (View) çalıştırıp alıyoruz
    cursor.execute("SELECT * FROM VW_RotaTercihleri")
    rota_verisi = cursor.fetchall()

    if rota_verisi:
        df_rota = pd.DataFrame(rota_verisi)
        
        # Ekranı ikiye bölüyoruz (Grafik daha geniş yer kaplasın diye [2, 1] oranında)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Rota isimlerine göre bir çubuk grafiği çiziyoruz
            st.bar_chart(data=df_rota, x='RotaAdi', y='ToplamKosuSayisi')
            
        with col2:
            # Tablonun sütun isimlerini düzeltip ekrana basıyoruz
            df_rota.rename(columns={'RotaAdi': 'Rota', 'ZorlukKatsayisi': 'Zorluk', 'OrtalamaSure_Dk': 'Ort. Süre (Dk)'}, inplace=True)
            st.dataframe(df_rota[['Rota', 'Zorluk', 'Ort. Süre (Dk)']], use_container_width=True, hide_index=True)