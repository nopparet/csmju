# =================================================================
#  setup_mysql.ps1 — ตั้งค่า MySQL สำหรับ Smart Kiosk
#  รัน: Right-click > "Run with PowerShell" (ในฐานะ Administrator)
#  หรือเปิด PowerShell as Admin แล้วพิมพ์:
#    cd "c:\Users\Lenovo\OneDrive\เอกสาร\smart-kiosk"
#    .\setup_mysql.ps1
# =================================================================

$mysql = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
$mysqlDir = Split-Path $mysql
$sqlDir = Join-Path $PSScriptRoot "backend\sql"

Write-Host "=== Smart Kiosk — MySQL Setup ===" -ForegroundColor Cyan
Write-Host ""

# ขอรหัสผ่าน root
$rootPass = Read-Host "กรุณาใส่รหัสผ่าน root ของ MySQL" -AsSecureString
$rootPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($rootPass))

# ทดสอบ login
Write-Host "`nกำลังทดสอบ login..." -ForegroundColor Yellow
$test = &$mysql -u root -p"$rootPassPlain" -e "SELECT 'OK';" 2>&1
if ($test -notmatch "OK") {
    Write-Host "ERROR: รหัสผ่านไม่ถูกต้อง หรือ MySQL ไม่พร้อม" -ForegroundColor Red
    Write-Host $test
    Read-Host "กด Enter เพื่อออก"
    exit 1
}
Write-Host "Login สำเร็จ!" -ForegroundColor Green

# รัน setup_db.sql (สร้าง database + user kiosk)
Write-Host "`nกำลังสร้าง database และ user..." -ForegroundColor Yellow
&$mysql -u root -p"$rootPassPlain" --default-character-set=utf8mb4 `
    -e (Get-Content "$sqlDir\setup_db.sql" -Raw) 2>&1
Write-Host "สร้าง database cs_kiosk และ user kiosk เสร็จแล้ว" -ForegroundColor Green

# รัน schema.sql
Write-Host "`nกำลังสร้างตาราง (schema)..." -ForegroundColor Yellow
&$mysql -u root -p"$rootPassPlain" --default-character-set=utf8mb4 `
    cs_kiosk < "$sqlDir\schema.sql" 2>&1
Write-Host "สร้างตารางเสร็จแล้ว" -ForegroundColor Green

# รัน seed.sql
Write-Host "`nกำลัง import ข้อมูลจริงของสาขา CS มจ. (seed)..." -ForegroundColor Yellow
&$mysql -u root -p"$rootPassPlain" --default-character-set=utf8mb4 `
    cs_kiosk < "$sqlDir\seed.sql" 2>&1
Write-Host "Import ข้อมูลเสร็จแล้ว" -ForegroundColor Green

# ตรวจสอบ
Write-Host "`nกำลังตรวจสอบข้อมูล..." -ForegroundColor Yellow
$check = &$mysql -u kiosk -pkiosk1234 cs_kiosk --default-character-set=utf8mb4 `
    -e "SELECT COUNT(*) as rooms FROM rooms; SELECT COUNT(*) as teachers FROM teachers; SELECT COUNT(*) as courses FROM courses; SELECT COUNT(*) as schedules FROM schedules;" 2>&1
Write-Host $check -ForegroundColor White

Write-Host ""
Write-Host "=== ตั้งค่าสำเร็จทั้งหมด! ===" -ForegroundColor Green
Write-Host "ไฟล์ .env ที่ backend/ ตั้งค่าไว้แล้ว:" -ForegroundColor White
Write-Host "  DB_USER=kiosk  DB_PASSWORD=kiosk1234  DB_NAME=cs_kiosk" -ForegroundColor Gray
Write-Host ""
Write-Host "ขั้นตอนต่อไป:" -ForegroundColor Cyan
Write-Host "  1. cd backend" -ForegroundColor White
Write-Host "  2. .venv\Scripts\activate" -ForegroundColor White
Write-Host "  3. uvicorn app.main:app --reload --port 8000" -ForegroundColor White
Write-Host "  4. เปิด http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Read-Host "กด Enter เพื่อออก"
