"""
gemini_chat.py — Gemini Flash fallback สำหรับ chatbot
ใช้เมื่อ rule-based ตอบไม่ได้ หรือ score ต่ำ
ส่ง context จาก DB ให้ Gemini รู้จักข้อมูลของสาขา
"""
# google-genai เป็น optional dependency — import แบบ lazy
# ถ้าไม่ได้ติดตั้ง หรือไม่มี GEMINI_API_KEY ระบบจะข้ามไปโดยอัตโนมัติ
try:
    import google.genai as genai
    from google.genai import types
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    _GENAI_AVAILABLE = False

from datetime import datetime
from sqlalchemy.orm import Session

from .config import GEMINI_API_KEY
from . import models
from .services import schedules_of_day, schedule_to_dict, weekday_key, WEEKDAY_TH

_client = None


def _get_client():
    global _client
    if not _GENAI_AVAILABLE:
        return None
    if _client is None:
        if not GEMINI_API_KEY:
            return None
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _build_context(db: Session) -> str:
    """สร้าง context จาก DB ให้ Gemini ใช้"""
    now = datetime.now()
    today_key = weekday_key(now.date())
    today_th = WEEKDAY_TH.get(today_key, "วันนี้")

    # ตารางวันนี้
    schedules = [schedule_to_dict(s) for s in schedules_of_day(db, today_key)]
    sched_lines = "\n".join(
        f"  {r['start_time']}-{r['end_time']} {r['course_code']} {r['course_name']} "
        f"(อ.{r['teacher']}, ห้อง {r['room']})"
        for r in schedules
    ) or "  ไม่มีคาบเรียน"

    # อาจารย์ทั้งหมด
    teachers = db.query(models.Teacher).all()
    teacher_lines = "\n".join(
        f"  - {t.name} โทร {t.phone or '-'} เวลาให้คำปรึกษา: {t.office_hours or 'ไม่ระบุ'}"
        for t in teachers if 'chorthip' not in (t.email or '')
    )

    # ห้องทั้งหมด
    rooms = db.query(models.Room).all()
    room_lines = "\n".join(
        f"  - {r.code}: {r.name} (ชั้น {r.floor}) — {r.hint or ''}"
        for r in rooms
    )

    # กิจกรรมใกล้มา
    activities = (db.query(models.Activity)
                  .filter(models.Activity.start_at >= now)
                  .order_by(models.Activity.start_at).limit(3).all())
    act_lines = "\n".join(
        f"  - {a.start_at.strftime('%d/%m %H:%M')} {a.title}" for a in activities
    ) or "  ไม่มีกิจกรรม"

    return f"""=== บริบทข้อมูลสาขาวิทยาการคอมพิวเตอร์ มหาวิทยาลัยแม่โจ้ ===
เวลาปัจจุบัน: {now.strftime('%H:%M')} น. วัน{today_th} {now.strftime('%d/%m/%Y')}
อาคาร: แม่โจ้ 60 ปี ชั้น 6 | เว็บไซต์: csmju.com | โทร: 053-873800
เปิดทำการ: จันทร์-ศุกร์ 08:30-16:30 น.

ตารางเรียน-สอนวัน{today_th}:
{sched_lines}

อาจารย์ประจำสาขา (ห้องพักอาจารย์อยู่ซ้ายสุดชั้น 6):
{teacher_lines}

ห้องในชั้น 6:
{room_lines}

กิจกรรมที่กำลังจะถึง:
{act_lines}

จำนวนนักศึกษาในระบบ: {db.query(models.Student).count()} คน (ปีการศึกษา 2566)
"""


def ask_gemini(db: Session, question: str) -> str | None:
    """
    ถาม Gemini พร้อม context จาก DB
    คืนค่า None ถ้าไม่มี API key หรือเกิด error
    """
    client = _get_client()
    if client is None:
        return None
    try:
        context = _build_context(db)
        system = (
            "คุณคือผู้ช่วยตอบคำถามของ kiosk สาขาวิทยาการคอมพิวเตอร์ มหาวิทยาลัยแม่โจ้ "
            "ตอบเป็นภาษาไทย กระชับ ชัดเจน ไม่เกิน 5 บรรทัด "
            "ใช้ข้อมูลจากบริบทที่ให้มาเท่านั้น "
            "ถ้าไม่มีข้อมูลในบริบท ให้บอกว่า 'ไม่มีข้อมูลในระบบ กรุณาติดต่อสำนักงานสาขา' "
            "ห้ามแต่งข้อมูลขึ้นเองโดยไม่มีในบริบท"
        )
        prompt = f"{context}\n\nคำถามจากผู้ใช้: {question}"
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.3,
                max_output_tokens=400,
            ),
        )
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini error] {e}")
        return None
