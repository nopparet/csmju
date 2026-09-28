# =================================================================
#  reset_mysql_root.ps1 — รีเซ็ตรหัสผ่าน root MySQL 8.0 บน Windows
#  ต้องรันในฐานะ Administrator
# =================================================================

$mysqlBin = "C:\Program Files\MySQL\MySQL Server 8.0\bin"
$mysqld   = "$mysqlBin\mysqld.exe"
$mysql    = "$mysqlBin\mysql.exe"
$dataDir  = "C:\ProgramData\MySQL\MySQL Server 8.0\Data"
$newPass  = "Admin1234!"   # รหัสผ่านใหม่ที่ต้องการ

Write-Host "=== รีเซ็ตรหัสผ่าน MySQL root ===" -ForegroundColor Cyan
Write-Host "รหัสผ่านใหม่จะเป็น: $newPass" -ForegroundColor Yellow
Write-Host ""

# 1. หยุด MySQL service
Write-Host "[1/5] หยุด MySQL service..." -ForegroundColor Yellow
Stop-Service MySQL80 -Force -ErrorAction SilentlyContinue
Start-Sleep 3
Write-Host "     หยุดแล้ว" -ForegroundColor Green

# 2. เขียน init file สำหรับรีเซ็ตรหัสผ่าน
$initFile = "$env:TEMP\mysql_init.sql"
@"
ALTER USER 'root'@'localhost' IDENTIFIED BY '$newPass';
FLUSH PRIVILEGES;
"@ | Out-File $initFile -Encoding ascii
Write-Host "[2/5] เขียน init file แล้ว: $initFile" -ForegroundColor Green

# 3. เริ่ม mysqld แบบ skip-grant-tables
Write-Host "[3/5] เริ่ม mysqld แบบ init-file..." -ForegroundColor Yellow
$proc = Start-Process -FilePath $mysqld `
    -ArgumentList "--init-file=`"$initFile`"", "--console", "--skip-networking" `
    -PassThru -WindowStyle Hidden
Start-Sleep 8
Write-Host "     เริ่มแล้ว (PID $($proc.Id))" -ForegroundColor Green

# 4. หยุด mysqld ที่รันชั่วคราว
Write-Host "[4/5] หยุด mysqld ชั่วคราว..." -ForegroundColor Yellow
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Start-Sleep 3
Write-Host "     หยุดแล้ว" -ForegroundColor Green

# 5. เริ่ม MySQL service ปกติ
Write-Host "[5/5] เริ่ม MySQL service ปกติ..." -ForegroundColor Yellow
Start-Service MySQL80
Start-Sleep 5

# ทดสอบ login ด้วยรหัสผ่านใหม่
$test = &$mysql -u root -p"$newPass" -e "SELECT 'OK';" 2>&1
if ($test -match "OK") {
    Write-Host ""
    Write-Host "สำเร็จ! รหัสผ่าน root ใหม่: $newPass" -ForegroundColor Green
    Write-Host ""
    Write-Host "ต่อไป รัน setup_mysql.ps1 แล้วใส่รหัสผ่าน: $newPass" -ForegroundColor Cyan
} else {
    Write-Host "ERROR: รีเซ็ตไม่สำเร็จ กรุณาลองรีเซ็ตด้วย MySQL Workbench" -ForegroundColor Red
    Write-Host $test -ForegroundColor Red
}

Remove-Item $initFile -ErrorAction SilentlyContinue
Read-Host "กด Enter เพื่อออก"
