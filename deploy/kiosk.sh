#!/bin/bash
# เปิด Chromium แบบ kiosk ชี้ไปที่หน้าเว็บที่ build แล้ว (รันบน Raspberry Pi 5)
xset s off; xset -dpms; xset s noblank          # ไม่ให้จอดับ
unclutter -idle 0.5 -root &                     # ซ่อนเคอร์เซอร์
chromium-browser --kiosk --incognito --noerrdialogs \
  --disable-session-crashed-bubble --disable-infobars \
  --check-for-update-interval=31536000 \
  http://localhost/
