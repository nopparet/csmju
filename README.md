# Smart Reception Kiosk — สาขาวิทยาการคอมพิวเตอร์ มหาวิทยาลัยแม่โจ้

คีออสก์หน้าสาขาวิทยาการคอมพิวเตอร์: นำทางในอาคาร, ตารางเรียน-สอน,
ผู้ช่วยตอบคำถามแบบ rule-based + Gemini AI Fallback, เช็คชื่อด้วย QR/บัตรนักศึกษา และสถิติผู้ใช้งาน
**ทำงานออฟไลน์ได้ทั้งหมดบน Raspberry Pi 5 เครื่องเดียว** — ปล่อย WiFi Hotspot ได้ในตัว

---

## โครงสร้างโปรเจกต์

```
smart-kiosk/
├── backend/                  FastAPI + SQLAlchemy + MariaDB
│   ├── app/
│   │   ├── main.py           ประกอบ router, สร้างตาราง, เตรียมคาบเรียนของวันนี้
│   │   ├── models.py         11 ตาราง (rooms, teachers, students, courses, ...)
│   │   ├── services.py       ฟังก์ชันร่วม (สถานะห้อง, คาบที่เปิดเช็คชื่อ)
│   │   ├── chatbot.py        เครื่องจับ intent แบบ rule-based
│   │   ├── gemini_chat.py    Gemini AI fallback (optional — ใช้เมื่อมี API key)
│   │   ├── config.py         โหลด .env
│   │   ├── database.py       SQLAlchemy engine + session
│   │   └── routers/          rooms, schedule, chat, attendance, stats
│   ├── sql/
│   │   ├── schema.sql        โครงสร้างฐานข้อมูล
│   │   └── seed.sql          ข้อมูลตัวอย่าง (ห้อง, อาจารย์, วิชา, ตาราง)
│   ├── .env.example          ตัวอย่างไฟล์ตั้งค่า
│   └── requirements.txt
├── frontend/                 React + Vite
│   └── src/screens/          Welcome, UserType, Menu, Navigate,
│                             Schedule, Chat, CheckIn, Dashboard
└── deploy/
    ├── install_rpi.sh        สคริปต์ติดตั้งอัตโนมัติบน Raspberry Pi 5
    ├── kiosk-api.service     systemd service สำหรับ FastAPI backend
    ├── kiosk.sh              เปิด Chromium แบบ kiosk mode
    └── make_qr.py            สร้าง QR Code สำหรับเช็คชื่อ
```

---

## การ Deploy บน Raspberry Pi 5 (วิธีอัตโนมัติ)

### สิ่งที่ต้องเตรียม
- Raspberry Pi 5 ติดตั้ง **Raspberry Pi OS 64-bit** พร้อม SSH เปิดไว้
- โน้ตบุ๊คและ Pi อยู่ใน **WiFi เดียวกัน**

### ขั้นตอน

**1. โอนโปรเจกต์ไป Pi (จาก Windows PowerShell):**
```powershell
scp -r "C:\path\to\smart-kiosk" pi_username@<IP_Pi>:/home/pi_username/
```

**2. SSH เข้า Pi แล้วรันสคริปต์ติดตั้ง:**
```bash
cd /home/<username>/smart-kiosk/deploy
sudo bash install_rpi.sh
```

สคริปต์จะติดตั้งครบอัตโนมัติ: MariaDB, Python venv, nginx, Node.js, systemd service

**3. รีบูต:**
```bash
sudo reboot
```

---

## การตั้งค่า WiFi Hotspot (แนะนำ)

ทำให้ Pi ปล่อย WiFi ได้เอง **ไม่ต้องพึ่ง Router** — พกไปให้ดูที่ไหนก็ได้

```bash
# รันบน Pi (SSH)
sudo nmcli con add type wifi ifname wlan0 con-name 'Smart-Kiosk-AP' \
    ssid 'Smart-Kiosk' mode ap ipv4.method shared \
    ipv4.addresses 10.42.0.1/24 \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk 'smartkiosk1234'
sudo nmcli con mod 'Smart-Kiosk-AP' connection.autoconnect yes
sudo nmcli con up 'Smart-Kiosk-AP'
```

| | ค่า |
|--|--|
| **WiFi SSID** | `Smart-Kiosk` |
| **WiFi Password** | `smartkiosk1234` |
| **URL หน้าเว็บ** | `http://10.42.0.1/` |
| **API Docs** | `http://10.42.0.1:8000/docs` |

---

## เริ่มใช้งานบน Windows (Development)

### 1. ฐานข้อมูล
```bash
mysql -u root -p < backend/sql/schema.sql
mysql -u root -p < backend/sql/seed.sql       # ข้อมูลตัวอย่าง
```

### 2. Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # แก้รหัสผ่าน DB ในไฟล์นี้
uvicorn app.main:app --reload --port 8000
```
เปิด http://localhost:8000/docs เพื่อลองยิง API ทุกตัว

### 3. Frontend
```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173 (proxy /api ไปที่ :8000)
```

---

## ไฟล์ .env

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=kiosk
DB_PASSWORD=kiosk1234
DB_NAME=cs_kiosk
CHECKIN_EARLY_MIN=15
CHECKIN_LATE_MIN=30
GEMINI_API_KEY=            # ถ้ามี key จะใช้ Gemini AI ช่วยตอบคำถาม (optional)
```

---

## สถาปัตยกรรมบน Raspberry Pi 5

```
Chromium (kiosk mode)
        │
      nginx :80
        │
   ┌────┴────────────┐
   │ /               │ /api (proxy)
   │                 │
/var/www/html/   FastAPI :8000
(React build)        │
                 MariaDB :3306
```

| Component | รายละเอียด |
|-----------|-----------|
| OS | Raspberry Pi OS 64-bit |
| Frontend | React + Vite → build เป็น static files |
| Web Server | nginx (serve static + reverse proxy API) |
| Backend | FastAPI + uvicorn (systemd service) |
| Database | MariaDB (เดิมใช้ MySQL) |
| AI Fallback | Gemini Flash (optional, ต้องมี API key) |

---

## API Reference

| Method | Endpoint | หน้าที่ |
|--------|----------|---------|
| GET | `/api/health` | Health check |
| GET | `/api/rooms?q=201` | ค้นห้อง + ตำแหน่งบนผัง + สถานะตอนนี้ |
| GET | `/api/rooms/teachers` | รายชื่ออาจารย์ + ห้องพัก |
| GET | `/api/schedule?day=mon&room=CS-201` | ตารางเรียน-สอน |
| GET | `/api/schedule/activities` | กิจกรรมที่กำลังจะถึง |
| POST | `/api/chat` | ถาม-ตอบ (rule-based + Gemini fallback) |
| GET | `/api/attendance/current` | คาบที่เปิดให้เช็คชื่อตอนนี้ |
| POST | `/api/attendance` | เช็คชื่อ (รหัส นศ. / UID บัตร / payload QR) |
| GET | `/api/stats?days=7` | สถิติผู้ใช้งาน + coverage ของบอท |
| POST | `/api/logs/visit` | บันทึกการเข้าใช้แต่ละเมนู |

---

## เพิ่มความสามารถให้บอท

**ไม่ต้องแก้โค้ด** ถ้าคำตอบเป็นข้อความคงที่ — เพิ่มแถวในตาราง `chat_intents`:

```sql
INSERT INTO chat_intents (intent_name, keywords, answer_template, priority)
VALUES ('wifi', 'wifi,ไวไฟ,อินเทอร์เน็ต,รหัสเน็ต',
        'ใช้ SSID: CS-Student รหัสผ่านขอที่สำนักงานสาขา', 5);
```

ถ้าคำตอบต้องดึงจากฐานข้อมูล ให้เขียนฟังก์ชัน `h_<ชื่อ>` ใน `app/chatbot.py`
แล้วลงทะเบียนใน dict `HANDLERS`

คำถามที่บอทจับ intent ไม่ได้จะถูกบันทึกลง `chat_logs` (answered = 0)
ดูได้จากหน้า Dashboard — ใช้เป็นข้อมูลวัดผลในเล่มรายงานได้

---

## สร้าง QR Code สำหรับเช็คชื่อ

```bash
cd deploy && python make_qr.py CLASS 12
```

payload รูปแบบ `KIOSK:CLASS:<session_id>` — backend รับได้ทั้ง payload นี้,
รหัสนักศึกษาล้วน และ UID จากบัตร

---

## กติกาการเช็คชื่อ

- รับเช็คชื่อตั้งแต่ 15 นาทีก่อนเริ่มคาบ ถึง 30 นาทีหลังเริ่มคาบ (แก้ได้ใน `.env`)
- เกิน 10 นาทีหลังเริ่มคาบ บันทึกเป็น "มาสาย"
- เช็คชื่อซ้ำไม่ได้ (unique key `ref_type + ref_id + student_id`)
- ไม่ได้ลงทะเบียนวิชานั้น จะบันทึกผลเป็น `denied` ไว้ตรวจสอบย้อนหลัง

---

## คำสั่ง Maintenance บน Pi

```bash
# ดูสถานะ service
sudo systemctl status kiosk-api

# ดู log แบบ real-time
sudo journalctl -u kiosk-api -f

# รีสตาร์ท backend
sudo systemctl restart kiosk-api

# อัปเดตโค้ด (หลัง git pull หรือแก้ไขไฟล์)
cd /home/<username>/smart-kiosk/frontend
npm run build && sudo cp -r dist/. /var/www/html/
sudo systemctl restart kiosk-api

# ตรวจสอบ DB
sudo mysql -u root -e "SHOW TABLES IN cs_kiosk;"
```

---

## สิ่งที่ยังต้องทำต่อ

- หน้า Admin สำหรับอัปโหลดตารางจาก Excel/CSV และเพิ่มข่าวกิจกรรม
- อ่านบัตรนักศึกษาผ่านเครื่องอ่าน USB (ส่วนใหญ่ทำงานเหมือนคีย์บอร์ด — รับค่าเข้าช่องกรอกได้เลย)
- ตั้ง cron สำรองฐานข้อมูลวันละครั้ง
- เพิ่ม GEMINI_API_KEY ใน `.env` เพื่อเปิดใช้ Gemini AI fallback ในบอท
