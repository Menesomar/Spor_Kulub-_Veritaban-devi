# 🏃‍♂️ Koşu Kulübü: Liderlik ve Takip Sistemi (KosuKulubuDB)

**Kocaeli Üniversitesi - Bilişim Sistemleri Mühendisliği Bölümü**
**TBL331: Veritabanı Yönetim Sistemleri - 2025-2026 Bahar Dönemi Projesi**

**Proje Ekibi:**
* Rıdvan Elen
* Muhammed Enes Omar

---

## 🎯 1. Problem Tanımı
Günümüzde spor kulüplerinde ve amatör koşu gruplarında üyelerin performans takibi, koşulan rotaların zorluk derecelerine göre adil bir şekilde puanlanması ve üyeler arası motivasyonun (rekabetin) canlı tutulması büyük bir problemdir. Mevcut sistemlerin karmaşık olması veya sadece bireysel takibe odaklanması, kulüp içi etkileşimi düşürmektedir. Bu proje; koşucuların verilerini merkezi bir veritabanında toplayarak, zorluk katsayılarına göre adil puanlama yapan ve üyeleri "Oyunlaştırma (Gamification)" mantığıyla farklı liglere yerleştiren dinamik bir rekabet ortamı yaratmayı hedefleyerek bu problemi çözmektedir.

## 🔍 2. Yapılan Araştırmalar
* **Oyunlaştırma ve Motivasyon:** Kullanıcıların spora devamlılığını sağlamak amacıyla e-spor ve mobil oyunlardaki "Lig (Bronz, Gümüş, Altın vb.)" sistemleri incelenmiş ve projeye entegre edilmiştir.
* **Adil Puanlama Algoritmaları:** Sadece mesafenin değil, rotanın coğrafi zorluğunun da (Zorluk Katsayısı) puana etki etmesi gerektiği araştırılmış ve puanlama formülü (`Mesafe * 10 * Zorluk`) geliştirilmiştir.
* **Hızlı ve Modern Arayüz Geliştirme:** Projenin kullanıcı arayüzü için Python tabanlı Streamlit kütüphanesi araştırılmış; veri görselleştirme ve veritabanı entegrasyonu açısından en verimli araç olduğuna karar verilmiştir.
* **Veri Bütünlüğü ve Güvenlik:** İmkansız hızlarda girilen koşu kayıtlarını (hileleri) engellemek adına veritabanı seviyesinde `CHECK` kısıtlamaları ve Stored Procedure içi kontroller araştırılıp uygulanmıştır.

## 🔄 3. Akış Şeması
*Uygulamanın temel işleyiş mantığı aşağıdaki akış şemasında gösterilmiştir:*

```mermaid
graph TD
    A[Kullanıcı Girişi / Kayıt] --> B{Giriş Başarılı mı?}
    B -- Hayır --> A
    B -- Evet --> C[Ana Kontrol Paneli]
    C --> D[Duyuruları Görüntüle]
    C --> E[Yeni Koşu Ekle]
    C --> F[Canlı Liderlik Tablosu]
    E --> G{Hile/Mantık Kontrolü}
    G -- Geçersiz Değer --> H[Hata Mesajı]
    G -- Geçerli Değer --> I[(Veritabanı: Kosular)]
    I --> J[Trigger: Puanı Hesapla]
    J --> K[Trigger: Ligi Güncelle]
    K --> F
