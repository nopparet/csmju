"""สร้างภาพ QR สำหรับคาบเรียน/กิจกรรม — ใช้ติดหน้าห้องหรือแสดงบนจอ
ใช้: python make_qr.py CLASS 12   ->  qr_CLASS_12.png
"""
import sys

import qrcode

kind = (sys.argv[1] if len(sys.argv) > 1 else "CLASS").upper()
ref_id = sys.argv[2] if len(sys.argv) > 2 else "1"
payload = f"KIOSK:{kind}:{ref_id}"

img = qrcode.make(payload)
out = f"qr_{kind}_{ref_id}.png"
img.save(out)
print("saved", out, "payload:", payload)
