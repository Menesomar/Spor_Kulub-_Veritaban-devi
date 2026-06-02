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
            port=os.getenv("DB_PORT", 3306),
            autocommit=True  # Listeyi anında güncelleyen ayar
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
    
    # Giriş ve Kayıt ekranlarını sekmelere ayırıyoruz
    tab1, tab2 = st.tabs(["🔑 Giriş Yap", "📝 Yeni Kayıt Oluştur"])
    
    # --- 1. GİRİŞ YAP SEKME ---
    with tab1:
        with st.form("login_form"):
            eposta = st.text_input("E-posta Adresi")
            sifre = st.text_input("Şifre", type="password")
            submit_button = st.form_submit_button("Sisteme Giriş Yap")
            
            if submit_button:
                login(eposta, sifre)
                
    # --- 2. KAYIT OL SEKME ---
    with tab2:
        st.subheader("Yeni Üye Kaydı")
        with st.form("kayit_form"):
            yeni_ad = st.text_input("Ad")
            yeni_soyad = st.text_input("Soyad")
            yeni_eposta = st.text_input("E-posta Adresi")
            yeni_cinsiyet = st.selectbox("Cinsiyet", ["Erkek (E)", "Kadın (K)"])
            yeni_sifre = st.text_input("Şifre", type="password")
            yeni_sifre_tekrar = st.text_input("Şifre (Tekrar)", type="password")
            
            kayit_btn = st.form_submit_button("Kayıt Ol")
            
            if kayit_btn:
                if yeni_sifre != yeni_sifre_tekrar:
                    st.error("Şifreler eşleşmiyor! Lütfen kontrol edin.")
                elif not yeni_ad or not yeni_soyad or not yeni_eposta or not yeni_sifre:
                    st.error("Lütfen tüm alanları doldurun.")
                else:
                    # Cinsiyet verisini veritabanındaki (E/K) formatına çevir
                    cinsiyet_kodu = "E" if "Erkek" in yeni_cinsiyet else "K"
                    
                    try:
                        cursor = conn.cursor()
                        # 1. Üyeyi veritabanına ekle (Rol varsayılan olarak 'Uye' atanacak)
                        insert_uye_query = """
                        INSERT INTO Uyeler (Ad, Soyad, Eposta, Cinsiyet, Sifre) 
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_uye_query, (yeni_ad, yeni_soyad, yeni_eposta, cinsiyet_kodu, yeni_sifre))
                        
                        # Eklenen yeni üyenin ID'sini otomatik al
                        yeni_uye_id = cursor.lastrowid
                        
                        # 2. Üyeyi Çaylak ligiyle (Lig_ID: 1) mevcut sezona dahil et
                        import datetime
                        mevcut_yil = datetime.datetime.now().year
                        insert_lig_query = """
                        INSERT INTO Uye_Sezon_Lig (Uye_ID, Lig_ID, Sezon_Yili, ToplamPuan) 
                        VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(insert_lig_query, (yeni_uye_id, 1, mevcut_yil, 0))
                        
                        conn.commit()
                        cursor.close()
                        
                        st.success("🎉 Kayıt başarıyla oluşturuldu! Şimdi 'Giriş Yap' sekmesinden sisteme girebilirsiniz.")
                        
                    except mysql.connector.IntegrityError:
                        st.error("Bu e-posta adresi zaten kullanımda! Lütfen başka bir e-posta deneyin.")
                    except Exception as e:
                        st.error(f"Kayıt işlemi sırasında bir hata oluştu: {e}")

else:
    # --- ANA SİSTEM (Giriş Yapıldıktan Sonra) ---
    st.sidebar.title(f"Hoş geldin, {st.session_state.kullanici_adi} 👋")
    st.sidebar.success(f"Yetki Seviyesi: **{st.session_state.rol}**")
    
    # Rol Bazlı Menü
    if st.session_state.rol == "Admin":
        menu = ["🏆 Liderlik Tablosu", "➕ Yeni Koşu Ekle (Admin)", "👤 Kendi Profilim"]
    else:
        menu = ["🏆 Liderlik Tablosu", "👤 Kendi Profilim"]
        
    secim = st.sidebar.radio("Sayfalar", menu)
    st.sidebar.markdown("---")
    if st.sidebar.button("Çıkış Yap 🚪"):
        logout()

    # --- 1. LİDERLİK TABLOSU (VIEW Kullanımı) ---
    if secim == "🏆 Liderlik Tablosu":
        st.header("🏆 Güncel Liderlik Tablosu")
        st.write("Bu tablo veritabanındaki `VW_CanliLigSiralama` view'ından anlık olarak çekilmektedir.")
        
        try:
            query = "SELECT * FROM VW_CanliLigSiralama"
            df = pd.read_sql(query, conn)
            # Veriyi Streamlit'in interaktif tablosunda göster (büyüklük, arama vs. otomatik)
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Tablo çekilirken hata oluştu: {e}")

    # --- 2. YENİ KOŞU EKLE (Stored Procedure ve Trigger Kullanımı) ---
    elif secim == "➕ Yeni Koşu Ekle (Admin)":
        st.header("➕ Sisteme Yeni Koşu Verisi Gir (Hile Korumalı)")
        st.write("Bu sayfada eklenen koşular `SP_YeniKosuEkle` prosedüründen geçer. Eğer veri mantıklıysa kaydedilir ve `TRG_PuanHesapla_Ve_LigGuncelle` trigger'ı puanı otomatik hesaplayıp ligi günceller.")
        
        try:
            cursor = conn.cursor(dictionary=True)
            # Rotaları getir
            cursor.execute("SELECT Rota_ID, RotaAdi, ZorlukKatsayisi FROM Rotalar") 
            rotalar = cursor.fetchall()
            rota_sozlugu = {f"{r['RotaAdi']} (Zorluk: {r['ZorlukKatsayisi']})": r['Rota_ID'] for r in rotalar}
            
            # Üyeleri getir (Kimin adına koşu eklenecekse onu seçmek için)
            cursor.execute("SELECT Uye_ID, Ad, Soyad FROM Uyeler")
            uyeler = cursor.fetchall()
            uye_sozlugu = {f"{u['Ad']} {u['Soyad']} (ID: {u['Uye_ID']})": u['Uye_ID'] for u in uyeler}
            cursor.close()

            with st.form("kosu_ekle_form"):
                secilen_uye = st.selectbox("Koşuyu Yapan Üye", list(uye_sozlugu.keys()))
                secilen_rota = st.selectbox("Koşulan Rota", list(rota_sozlugu.keys()))
                
                col1, col2 = st.columns(2)
                mesafe_km = col1.number_input("Mesafe (KM)", min_value=0.1, step=0.1, format="%.1f")
                sure_dk = col2.number_input("Koşu Süresi (Dakika)", min_value=1, step=1)
                
                kaydet_btn = st.form_submit_button("Koşuyu Kaydet (Procedure Çalıştır)")
                
                if kaydet_btn:
                    uye_id = uye_sozlugu[secilen_uye]
                    rota_id = rota_sozlugu[secilen_rota]
                    
                    try:
                        cursor = conn.cursor()
                        # Normal INSERT yerine Stored Procedure'ü çağırıyoruz (Hile Koruması için)
                        cursor.callproc('SP_YeniKosuEkle', (uye_id, rota_id, mesafe_km, sure_dk))
                        conn.commit()
                        cursor.close()
                        st.success("🎉 Koşu başarıyla eklendi! Trigger çalıştı, puanlar hesaplandı ve liderlik tablosu güncellendi.")
                    except mysql.connector.Error as err:
                        # Eğer Pace < 2.0 ise Stored Procedure hata fırlatacak, onu burada yakalayıp ekrana basıyoruz
                        st.error(f"Kayıt Reddedildi: {err.msg}")
                        
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")

    # --- 3. KENDİ PROFİLİM (Bireysel Geçmiş) ---
    elif secim == "👤 Kendi Profilim":
        st.header(f"👤 {st.session_state.kullanici_adi} - Profil ve Koşu Geçmişi")
        
        try:
            # Üyenin lig durumunu çek
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT L.LigAdi, USL.ToplamPuan 
                FROM Uye_Sezon_Lig USL 
                JOIN Ligler L ON USL.Lig_ID = L.Lig_ID 
                WHERE USL.Uye_ID = %s AND USL.Sezon_Yili = %s
            """, (st.session_state.kullanici_id, 2026)) # Örnek sezon yılı 2026
            lig_durumu = cursor.fetchone()
            cursor.close()
            
            if lig_durumu:
                col1, col2 = st.columns(2)
                col1.metric("Şu Anki Liginiz", lig_durumu['LigAdi'])
                col2.metric("Toplam Puanınız", lig_durumu['ToplamPuan'])
            
            st.subheader("Geçmiş Koşularım")
            # Kişinin kendi koşularını listele
            query = f"""
                SELECT R.RotaAdi, K.KosuTarihi, K.Mesafe_KM, K.Sure_Dakika, K.KazanilanPuan 
                FROM Kosular K 
                JOIN Rotalar R ON K.Rota_ID = R.Rota_ID 
                WHERE K.Uye_ID = {st.session_state.kullanici_id}
                ORDER BY K.KosuTarihi DESC
            """
            df_gecmis = pd.read_sql(query, conn)
            st.dataframe(df_gecmis, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"Profil bilgileri yüklenemedi: {e}")