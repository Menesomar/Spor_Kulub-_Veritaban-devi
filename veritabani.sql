-- 1. Veritabanını Oluşturma ve Seçme
CREATE DATABASE IF NOT EXISTS KosuKulubuDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE KosuKulubuDB;

-- ==========================================
-- TABLO OLUŞTURMA (5N Kuralına Uygun ve Kısıtlamalı)
-- ==========================================

-- Tablo 1: Ligler
CREATE TABLE Ligler (
    Lig_ID INT AUTO_INCREMENT PRIMARY KEY,
    LigAdi VARCHAR(50) NOT NULL UNIQUE,
    Min_Puan_Sart INT NOT NULL DEFAULT 0 CHECK (Min_Puan_Sart >= 0)
);

-- Tablo 2: Uyeler
CREATE TABLE Uyeler (
    Uye_ID INT AUTO_INCREMENT PRIMARY KEY,
    Ad VARCHAR(50) NOT NULL,
    Soyad VARCHAR(50) NOT NULL,
    Eposta VARCHAR(100) NOT NULL UNIQUE,
    Cinsiyet CHAR(1) NOT NULL CHECK (Cinsiyet IN ('E', 'K')),
    KayitTarihi DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tablo 3: Rotalar
CREATE TABLE Rotalar (
    Rota_ID INT AUTO_INCREMENT PRIMARY KEY,
    RotaAdi VARCHAR(100) NOT NULL,
    ZorlukKatsayisi DECIMAL(3,1) NOT NULL CHECK (ZorlukKatsayisi BETWEEN 1.0 AND 3.0)
);

-- Tablo 4: Uye_Sezon_Lig (Köprü Tablosu - Lig Geçmişi)
CREATE TABLE Uye_Sezon_Lig (
    Kayit_ID INT AUTO_INCREMENT PRIMARY KEY,
    Uye_ID INT NOT NULL,
    Lig_ID INT NOT NULL,
    Sezon_Yili INT NOT NULL,
    ToplamPuan INT DEFAULT 0 CHECK (ToplamPuan >= 0),
    FOREIGN KEY (Uye_ID) REFERENCES Uyeler(Uye_ID) ON DELETE CASCADE,
    FOREIGN KEY (Lig_ID) REFERENCES Ligler(Lig_ID) ON DELETE RESTRICT,
    UNIQUE (Uye_ID, Sezon_Yili) -- Bir üye bir sezonda tek bir aktif kayda sahip olabilir
);

-- Tablo 5: Kosular (İşlem Tablosu)
CREATE TABLE Kosular (
    Kosu_ID INT AUTO_INCREMENT PRIMARY KEY,
    Uye_ID INT NOT NULL,
    Rota_ID INT NOT NULL,
    KosuTarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
    Mesafe_KM DECIMAL(5,2) NOT NULL CHECK (Mesafe_KM > 0),
    Sure_Dakika INT NOT NULL CHECK (Sure_Dakika > 0),
    KazanilanPuan INT DEFAULT 0,
    FOREIGN KEY (Uye_ID) REFERENCES Uyeler(Uye_ID) ON DELETE CASCADE,
    FOREIGN KEY (Rota_ID) REFERENCES Rotalar(Rota_ID) ON DELETE RESTRICT
);

-- ==========================================
-- INDEX UYGULAMALARI
-- ==========================================
CREATE INDEX IDX_Uyeler_Eposta ON Uyeler(Eposta);
CREATE INDEX IDX_Kosular_Tarih ON Kosular(KosuTarihi);

-- ==========================================
-- VIEW UYGULAMALARI (Raporlama)
-- ==========================================

-- View 1: Arayüz için Canlı Liderlik Tablosu
CREATE VIEW VW_CanliLigSiralama AS
SELECT 
    U.Ad, 
    U.Soyad, 
    L.LigAdi, 
    USL.ToplamPuan, 
    USL.Sezon_Yili,
    IFNULL(SUM(K.Mesafe_KM), 0) AS ToplamKosulan_KM
FROM Uye_Sezon_Lig USL
JOIN Uyeler U ON USL.Uye_ID = U.Uye_ID
JOIN Ligler L ON USL.Lig_ID = L.Lig_ID
LEFT JOIN Kosular K ON U.Uye_ID = K.Uye_ID AND YEAR(K.KosuTarihi) = USL.Sezon_Yili
GROUP BY U.Uye_ID, U.Ad, U.Soyad, L.LigAdi, USL.ToplamPuan, USL.Sezon_Yili
ORDER BY USL.ToplamPuan DESC;

-- View 2: Rota İstatistikleri
CREATE VIEW VW_RotaTercihleri AS
SELECT 
    R.RotaAdi, 
    R.ZorlukKatsayisi, 
    COUNT(K.Kosu_ID) AS ToplamKosuSayisi,
    ROUND(AVG(K.Sure_Dakika), 1) AS OrtalamaSure_Dk
FROM Rotalar R
LEFT JOIN Kosular K ON R.Rota_ID = K.Rota_ID
GROUP BY R.Rota_ID, R.RotaAdi, R.ZorlukKatsayisi;

-- ==========================================
-- STORED PROCEDURE UYGULAMALARI (İş Mantığı)
-- ==========================================
DELIMITER //

-- Procedure 1: Hile Kontrollü Yeni Koşu Ekleme
CREATE PROCEDURE SP_YeniKosuEkle(
    IN p_Uye_ID INT,
    IN p_Rota_ID INT,
    IN p_Mesafe_KM DECIMAL(5,2),
    IN p_Sure_Dakika INT
)
BEGIN
    DECLARE v_Pace DECIMAL(5,2);
    
    -- Pace hesapla (KM başına dakika)
    SET v_Pace = p_Sure_Dakika / p_Mesafe_KM;
    
    -- Eğer pace 2.0'dan düşükse (Dünya rekorundan bile hızlı), işlemi iptal et (Hile Koruması)
    IF v_Pace < 2.0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Hata: Mantıksız koşu süresi (Hile Koruması)!';
    ELSE
        -- Mantıklıysa kaydı ekle
        INSERT INTO Kosular (Uye_ID, Rota_ID, Mesafe_KM, Sure_Dakika) 
        VALUES (p_Uye_ID, p_Rota_ID, p_Mesafe_KM, p_Sure_Dakika);
    END IF;
END //

DELIMITER ;

-- ==========================================
-- TRIGGER UYGULAMALARI (Otomasyon)
-- ==========================================
DELIMITER //

-- Trigger: Koşu eklendiğinde puanı hesapla, sezona ekle ve gerekiyorsa lig atlat
CREATE TRIGGER TRG_PuanHesapla_Ve_LigGuncelle
BEFORE INSERT ON Kosular
FOR EACH ROW
BEGIN
    DECLARE v_Zorluk DECIMAL(3,1);
    DECLARE v_Puan INT;
    DECLARE v_MevcutPuan INT;
    DECLARE v_YeniLig_ID INT;
    
    -- Rotanın zorluk derecesini al
    SELECT ZorlukKatsayisi INTO v_Zorluk FROM Rotalar WHERE Rota_ID = NEW.Rota_ID;
    
    -- Puan formülü: (Mesafe * 10) * Zorluk Katsayısı
    SET v_Puan = CAST((NEW.Mesafe_KM * 10 * v_Zorluk) AS SIGNED);
    SET NEW.KazanilanPuan = v_Puan;
    
    -- Üyenin mevcut sezon puanını güncelle
    UPDATE Uye_Sezon_Lig 
    SET ToplamPuan = ToplamPuan + v_Puan 
    WHERE Uye_ID = NEW.Uye_ID AND Sezon_Yili = YEAR(CURRENT_DATE);
    
    -- Üyenin yeni toplam puanını al
    SELECT ToplamPuan INTO v_MevcutPuan 
    FROM Uye_Sezon_Lig 
    WHERE Uye_ID = NEW.Uye_ID AND Sezon_Yili = YEAR(CURRENT_DATE);
    
    -- Puanın yettiği en yüksek ligi bul
    SELECT Lig_ID INTO v_YeniLig_ID 
    FROM Ligler 
    WHERE Min_Puan_Sart <= v_MevcutPuan 
    ORDER BY Min_Puan_Sart DESC LIMIT 1;
    
    -- Üyenin ligini güncelle
    UPDATE Uye_Sezon_Lig 
    SET Lig_ID = v_YeniLig_ID 
    WHERE Uye_ID = NEW.Uye_ID AND Sezon_Yili = YEAR(CURRENT_DATE);
END //

DELIMITER ;

-- ==========================================
-- DUMMY DATA (Test Verileri - Her tablo için 10 adet)
-- ==========================================

-- Ligler (10 Adet)
INSERT INTO Ligler (LigAdi, Min_Puan_Sart) VALUES 
('Çaylak', 0), ('Amatör', 100), ('Bronz', 250), ('Gümüş', 500), ('Altın', 1000), 
('Platin', 1500), ('Elit', 2500), ('Master', 4000), ('Şampiyon', 6000), ('Efsane', 10000);

-- Uyeler (10 Adet)
INSERT INTO Uyeler (Ad, Soyad, Eposta, Cinsiyet) VALUES 
('Ali', 'Yılmaz', 'ali.yilmaz@mail.com', 'E'), ('Ayşe', 'Kaya', 'ayse.kaya@mail.com', 'K'),
('Mehmet', 'Demir', 'mehmet.d@mail.com', 'E'), ('Fatma', 'Çelik', 'fatma.celik@mail.com', 'K'),
('Ahmet', 'Şahin', 'ahmet.s@mail.com', 'E'), ('Zeynep', 'Öztürk', 'zeynep.oz@mail.com', 'K'),
('Can', 'Arslan', 'can.arslan@mail.com', 'E'), ('Elif', 'Doğan', 'elif.dogan@mail.com', 'K'),
('Burak', 'Güneş', 'burak.gunes@mail.com', 'E'), ('Ceren', 'Yıldız', 'ceren.yildiz@mail.com', 'K');

-- Rotalar (10 Adet)
INSERT INTO Rotalar (RotaAdi, ZorlukKatsayisi) VALUES 
('Moda Sahil Yolu', 1.0), ('Belgrad Ormanı 6K', 1.5), ('Caddebostan Parkuru', 1.0), 
('Maçka Parkı Yokuş', 2.0), ('Aydos Ormanı Trail', 2.5), ('Polonezköy Tabiat Parkı', 1.8),
('Haliç Çevresi', 1.2), ('Çamlıca Tepesi Tırmanış', 2.8), ('Maltepe Veledrom', 1.0), ('Uludağ Zirve Rotası', 3.0);

-- Uye_Sezon_Lig Başlangıç Kayıtları (10 Adet - Herkes Çaylak liginde başlar)
INSERT INTO Uye_Sezon_Lig (Uye_ID, Lig_ID, Sezon_Yili, ToplamPuan) VALUES 
(1, 1, 2026, 0), (2, 1, 2026, 0), (3, 1, 2026, 0), (4, 1, 2026, 0), (5, 1, 2026, 0), 
(6, 1, 2026, 0), (7, 1, 2026, 0), (8, 1, 2026, 0), (9, 1, 2026, 0), (10, 1, 2026, 0);

-- Kosular (10 Adet - Bu kayıtlar girildiğinde Trigger çalışıp puanları/ligleri güncelleyecektir)
INSERT INTO Kosular (Uye_ID, Rota_ID, Mesafe_KM, Sure_Dakika) VALUES 
(1, 1, 5.0, 25), (2, 2, 6.0, 35), (3, 4, 3.0, 20), (4, 5, 10.0, 65), (5, 3, 5.0, 22), 
(6, 6, 8.0, 45), (7, 8, 4.0, 30), (8, 1, 10.0, 50), (9, 2, 6.0, 32), (10, 10, 15.0, 120);