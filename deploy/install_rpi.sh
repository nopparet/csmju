#!/bin/bash
# =============================================================================
#  Smart Kiosk — สคริปต์ติดตั้งอัตโนมัติบน Raspberry Pi 5
#  รันด้วย: bash install_rpi.sh
#  ต้องรันด้วยสิทธิ์ sudo หรือเป็น user pi ที่มี sudo
# =============================================================================

set -e  # หยุดทันทีถ้ามีข้อผิดพลาด

# ---------- สี ----------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC}  $1"; exit 1; }

# ---------- ตัวแปร ----------
APP_DIR="/home/pi/smart-kiosk"
VENV_DIR="$APP_DIR/backend/.venv"
DB_NAME="cs_kiosk"
DB_USER="kiosk"
DB_PASS="kiosk1234"   # ← เปลี่ยนรหัสผ่านได้ที่นี่
NGINX_CONF="/etc/nginx/sites-available/kiosk"
SERVICE_SRC="$APP_DIR/deploy/kiosk-api.service"
SERVICE_DEST="/etc/systemd/system/kiosk-api.service"

echo ""
echo "=================================================="
echo "   Smart Kiosk — ติดตั้งบน Raspberry Pi 5"
echo "=================================================="
echo ""

# ตรวจว่ารันด้วย sudo
if [ "$EUID" -ne 0 ]; then
    error "กรุณารันสคริปต์ด้วย sudo: sudo bash install_rpi.sh"
fi

# ตรวจ user pi มีอยู่
if ! id "pi" &>/dev/null; then
    warn "ไม่พบ user 'pi' — จะใช้ user ปัจจุบัน: $SUDO_USER"
    PI_USER="$SUDO_USER"
else
    PI_USER="pi"
fi
APP_DIR="/home/$PI_USER/smart-kiosk"
VENV_DIR="$APP_DIR/backend/.venv"
SERVICE_SRC="$APP_DIR/deploy/kiosk-api.service"

# =============================================================================
# 1. อัปเดต OS และติดตั้ง Package พื้นฐาน
# =============================================================================
info "1/7 อัปเดต package list..."
apt-get update -qq

info "    ติดตั้ง: git, python3-venv, nodejs, npm, nginx, mariadb-server, unclutter..."
apt-get install -y -qq \
    git \
    python3 python3-pip python3-venv \
    nodejs npm \
    nginx \
    mariadb-server \
    unclutter \
    curl \
    2>/dev/null
ok "ติดตั้ง package สำเร็จ"

# =============================================================================
# 2. Clone / อัปเดต โปรเจกต์
# =============================================================================
info "2/7 คัดลอกโปรเจกต์..."

if [ -d "$APP_DIR" ]; then
    warn "โฟลเดอร์ $APP_DIR มีอยู่แล้ว — ข้ามขั้นตอนนี้"
    warn "ถ้าต้องการอัปเดตโค้ด ให้รัน: cd $APP_DIR && git pull"
else
    # ถ้าโปรเจกต์อยู่ใน USB/SD: คัดลอกจากสคริปต์ปัจจุบัน
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    
    if [ -f "$PROJECT_ROOT/backend/requirements.txt" ]; then
        info "    คัดลอกจาก $PROJECT_ROOT → $APP_DIR"
        cp -r "$PROJECT_ROOT" "$APP_DIR"
        chown -R "$PI_USER:$PI_USER" "$APP_DIR"
    else
        error "ไม่พบโปรเจกต์ที่ $PROJECT_ROOT\nวาง smart-kiosk/ ใน /home/$PI_USER/ แล้วรันใหม่"
    fi
fi
ok "โปรเจกต์พร้อม: $APP_DIR"

# =============================================================================
# 3. ตั้งค่าฐานข้อมูล MariaDB
# =============================================================================
info "3/7 ตั้งค่าฐานข้อมูล MariaDB..."

systemctl enable mariadb --quiet
systemctl start mariadb

# สร้าง DB + User + ให้สิทธิ์
mysql -u root <<SQL
CREATE DATABASE IF NOT EXISTS ${DB_NAME}
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

# โหลด schema + seed
mysql -u root "$DB_NAME" < "$APP_DIR/backend/sql/schema.sql" 2>/dev/null || true
mysql -u root "$DB_NAME" < "$APP_DIR/backend/sql/seed.sql"   2>/dev/null || true
ok "ฐานข้อมูล '$DB_NAME' พร้อมใช้งาน"

# =============================================================================
# 4. ตั้งค่า Backend (Python venv + .env)
# =============================================================================
info "4/7 ตั้งค่า Backend..."

# สร้าง virtual environment
sudo -u "$PI_USER" python3 -m venv "$VENV_DIR"

# ติดตั้ง Python package
sudo -u "$PI_USER" "$VENV_DIR/bin/pip" install --upgrade pip --quiet
sudo -u "$PI_USER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/backend/requirements.txt" --quiet
ok "ติดตั้ง Python package สำเร็จ"

# สร้างไฟล์ .env
ENV_FILE="$APP_DIR/backend/.env"
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" <<ENV
DB_HOST=localhost
DB_PORT=3306
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASS}
DB_NAME=${DB_NAME}
CHECKIN_EARLY_MIN=15
CHECKIN_LATE_MIN=30
ENV
    chown "$PI_USER:$PI_USER" "$ENV_FILE"
    ok "สร้าง .env สำเร็จ"
else
    warn ".env มีอยู่แล้ว — ไม่เขียนทับ"
fi

# =============================================================================
# 5. Build Frontend + ติดตั้ง nginx
# =============================================================================
info "5/7 Build Frontend (React + Vite)..."

# ติดตั้ง npm package
cd "$APP_DIR/frontend"
sudo -u "$PI_USER" npm install --silent
sudo -u "$PI_USER" npm run build --silent
ok "Build frontend สำเร็จ → dist/"

# คัดลอกไปที่ /var/www/html
info "    คัดลอก dist/ → /var/www/html/..."
rm -rf /var/www/html/*
cp -r "$APP_DIR/frontend/dist/." /var/www/html/
chown -R www-data:www-data /var/www/html/

# สร้าง nginx config
info "    ตั้งค่า nginx..."
cat > "$NGINX_CONF" <<'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    root /var/www/html;
    index index.html;

    # React SPA — ทุก route ชี้ไปที่ index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy /api → FastAPI
    location /api {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_read_timeout 30s;
    }
}
NGINX

# เปิดใช้ site
ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/kiosk
rm -f /etc/nginx/sites-enabled/default  # เอา default ออก

nginx -t && systemctl enable nginx --quiet && systemctl restart nginx
ok "nginx พร้อมใช้งาน"

# =============================================================================
# 6. ลงทะเบียน systemd service สำหรับ Backend
# =============================================================================
info "6/7 ตั้งค่า systemd service..."

# สร้าง service file ใหม่ (ใช้ user และ path ที่ถูกต้อง)
cat > "$SERVICE_DEST" <<SERVICE
[Unit]
Description=Smart Kiosk API (FastAPI)
After=network.target mariadb.service

[Service]
User=${PI_USER}
WorkingDirectory=${APP_DIR}/backend
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable kiosk-api --quiet
systemctl restart kiosk-api
sleep 2

# ตรวจสอบว่า service รันได้
if systemctl is-active --quiet kiosk-api; then
    ok "kiosk-api.service รันอยู่ ✓"
else
    warn "kiosk-api.service มีปัญหา — ดู log ด้วย: journalctl -u kiosk-api -n 30"
fi

# =============================================================================
# 7. ตั้งค่า Kiosk Mode (Chromium เปิดอัตโนมัติเมื่อ login)
# =============================================================================
info "7/7 ตั้งค่า Kiosk Mode (auto-start Chromium)..."

AUTOSTART_DIR="/home/$PI_USER/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

# สร้าง .desktop ไฟล์ให้ Chromium เปิดอัตโนมัติ
cat > "$AUTOSTART_DIR/kiosk.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Smart Kiosk
Exec=/home/${PI_USER}/smart-kiosk/deploy/kiosk.sh
X-GNOME-Autostart-enabled=true
DESKTOP

chown -R "$PI_USER:$PI_USER" "$AUTOSTART_DIR"

# ทำให้ kiosk.sh รันได้
chmod +x "$APP_DIR/deploy/kiosk.sh"
chown "$PI_USER:$PI_USER" "$APP_DIR/deploy/kiosk.sh"
ok "Kiosk mode ตั้งค่าแล้ว"

# =============================================================================
# สรุป
# =============================================================================
echo ""
echo -e "${GREEN}=================================================="
echo "   ติดตั้งสำเร็จ!"
echo "=================================================="
echo -e "${NC}"
echo "  Backend API : http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "  Frontend    : http://$(hostname -I | awk '{print $1}')/"
echo "  Health check: http://$(hostname -I | awk '{print $1}'):8000/api/health"
echo ""
echo "  ตรวจสอบ service:"
echo "    sudo systemctl status kiosk-api"
echo "    sudo journalctl -u kiosk-api -f"
echo ""
echo -e "${YELLOW}  รีบูต Raspberry Pi เพื่อเปิด Kiosk Mode:"
echo -e "    sudo reboot${NC}"
echo ""
