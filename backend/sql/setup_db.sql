-- ============================================================
--  สคริปต์นี้ใช้หลังจากรีเซ็ต root หรือรู้รหัสผ่าน root แล้ว
--  คำสั่ง: "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < setup_db.sql
-- ============================================================

-- 1. สร้างฐานข้อมูล
CREATE DATABASE IF NOT EXISTS cs_kiosk
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 2. สร้าง user 'kiosk' ถ้ายังไม่มี
CREATE USER IF NOT EXISTS 'kiosk'@'localhost' IDENTIFIED BY 'kiosk1234';

-- 3. ให้สิทธิ์เต็มบน cs_kiosk เท่านั้น
GRANT ALL PRIVILEGES ON cs_kiosk.* TO 'kiosk'@'localhost';
FLUSH PRIVILEGES;

SELECT 'Setup OK: database=cs_kiosk, user=kiosk, password=kiosk1234' AS result;
