import streamlit as st
import mysql.connector
import pandas as pd
import os
import datetime
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

# Sayfa Ayarları
st.set_page_config(page_title="Koşu Kulübü Ligi", page_icon="🏃‍♂️", layout="wide")

# Veritabanı Bağlantısı (autocommit eklendi)
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
    st.title("🏃‍♂️ Koşu Kulübü Sistemine Giriş")
    st.write("Sisteme giriş yapabilir veya yeni bir hesap oluşturabilirsiniz.")
    
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Yeni Kayıt Oluştur"])
    
    # --- GİRİŞ YAP SEKME ---
    with tab1:
        with st.form("login_form"):
            eposta = st.text_input("E-posta Adresi")
            sifre = st.text_input("Şifre", type="password")
            if st.form_submit_button("Sisteme Giriş Yap"):
                login(eposta, sifre)
                
    # --- KAYIT OL SEKME ---
    with tab2:
        st.subheader("Yeni Üye Kaydı")
        with st.form("kayit_form"):
            yeni_ad = st.text_input("Ad")
            yeni_soyad = st.text_input("Soyad")
            yeni_eposta = st.text_input("E-posta Adresi")
            yeni_cinsiyet = st.selectbox("Cinsiyet", ["Erkek (E)", "Kadın (K)"])
            yeni_sifre = st.text_input("Şifre", type="password")
            yeni_sifre_tekrar = st.text_input("Şifre (Tekrar)", type="password")
            
            if st.form_submit_button("Kayıt Ol"):
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
    st.sidebar.title(f"Hoş geldin, {st.session_state.kullanici_adi} 👋")
    st.sidebar.success(f"Yetki Seviyesi: **{st.session_state.rol}**")
    
    if st.session_state.rol == "Admin":
        menu = ["🏆 Liderlik Tablosu", "➕ Yeni Koşu Ekle (Admin)", "⚖️ Ceza & Lig Düşürme", "👥 Tüm Üyeler", "👤 Kendi Profilim"]
    else:
        menu = ["🏆 Liderlik Tablosu", "👤 Kendi Profilim"]
        
    secim = st.sidebar.radio("Sayfalar", menu)
    st.sidebar.markdown("---")
    if st.sidebar.button("Çıkış Yap 🚪"):
        logout()

    # --- 1. LİDERLİK TABLOSU ---
    if secim == "🏆 Liderlik Tablosu":
        st.header("🏆 Liglere Göre Liderlik Tablosu")
        try:
            query = "SELECT * FROM VW_CanliLigSiralama"
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                aktif_ligler = df['LigAdi'].unique().tolist()
                sekmeler = st.tabs([f"🏅 {lig}" for lig in aktif_ligler])
                for sekme, lig_adi in zip(sekmeler, aktif_ligler):
                    with sekme:
                        lig_verisi = df[df['LigAdi'] == lig_adi].drop(columns=['LigAdi'])
                        st.dataframe(lig_verisi, use_container_width=True, hide_index=True)
            else:
                st.info("Tabloda veri yok.")
        except Exception as e:
            st.error(f"Tablo çekilirken hata oluştu: {e}")

    # --- 2. YENİ KOŞU EKLE ---
    elif secim == "➕ Yeni Koşu Ekle (Admin)":
        st.header("➕ Sisteme Yeni Koşu Verisi Gir (Hile Korumalı)")
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT Rota_ID, RotaAdi, ZorlukKatsayisi FROM Rotalar") 
            rotalar = cursor.fetchall()
            rota_sozlugu = {f"{r['RotaAdi']} (Zorluk: {r['ZorlukKatsayisi']})": r['Rota_ID'] for r in rotalar}
            
            cursor.execute("SELECT Uye_ID, Ad, Soyad FROM Uyeler")
            uyeler = cursor.fetchall()
            uye_sozlugu = {f"{u['Ad']} {u['Soyad']} (ID: {u['Uye_ID']})": u['Uye_ID'] for u in uyeler}
            cursor.close()

            # FORM BURADA TEK SEFER TANIMLANDI
            with st.form("kosu_ekle_form"):
                secilen_uye = st.selectbox("Koşuyu Yapan Üye", list(uye_sozlugu.keys()))
                secilen_rota = st.selectbox("Koşulan Rota", list(rota_sozlugu.keys()))
                
                col1, col2 = st.columns(2)
                mesafe_km = col1.number_input("Mesafe (KM)", min_value=0.1, step=0.1, format="%.1f")
                sure_dk = col2.number_input("Koşu Süresi (Dakika)", min_value=1, step=1)
                
                if st.form_submit_button("Koşuyu Kaydet"):
                    try:
                        cursor = conn.cursor()
                        cursor.callproc('SP_YeniKosuEkle', (uye_sozlugu[secilen_uye], rota_sozlugu[secilen_rota], mesafe_km, sure_dk))
                        st.success("🎉 Koşu eklendi! Trigger çalıştı, lig durumu güncellendi.")
                    except mysql.connector.Error as err:
                        st.error(f"Kayıt Reddedildi: {err.msg}")
        except Exception as e:
            st.error(f"Hata: {e}")

    # --- 3. CEZA VE LİG DÜŞÜRME ---
    elif secim == "⚖️ Ceza & Lig Düşürme":
        st.header("⚖️ Ceza Puanı Uygula ve Küme Düşür")
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

    # --- 4. TÜM ÜYELER ---
    elif secim == "👥 Tüm Üyeler":
        st.header("👥 Kulüp Üyeleri Yönetimi")
        try:
            df_uyeler = pd.read_sql("SELECT Uye_ID, Ad, Soyad, Eposta, Rol, Cinsiyet, KayitTarihi FROM Uyeler ORDER BY Uye_ID DESC", conn)
            st.dataframe(df_uyeler, use_container_width=True, hide_index=True)
        except Exception as e: pass

    # --- 5. KENDİ PROFİLİM ---
    elif secim == "👤 Kendi Profilim":
        st.header(f"👤 {st.session_state.kullanici_adi} - Profil")
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT L.LigAdi, USL.ToplamPuan FROM Uye_Sezon_Lig USL JOIN Ligler L ON USL.Lig_ID = L.Lig_ID WHERE USL.Uye_ID = %s AND USL.Sezon_Yili = %s", (st.session_state.kullanici_id, datetime.datetime.now().year))
            lig_durumu = cursor.fetchone()
            if lig_durumu:
                col1, col2 = st.columns(2)
                col1.metric("Liginiz", lig_durumu['LigAdi'])
                col2.metric("Puanınız", lig_durumu['ToplamPuan'])
            
            query = f"SELECT R.RotaAdi, K.KosuTarihi, K.Mesafe_KM, K.Sure_Dakika, K.KazanilanPuan FROM Kosular K JOIN Rotalar R ON K.Rota_ID = R.Rota_ID WHERE K.Uye_ID = {st.session_state.kullanici_id} ORDER BY K.KosuTarihi DESC"
            df_gecmis = pd.read_sql(query, conn)
            st.dataframe(df_gecmis, use_container_width=True, hide_index=True)
        except Exception as e: pass