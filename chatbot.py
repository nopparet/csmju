"""
Chatbot แบบ rule-based
ขั้นตอน: normalize -> extract entity -> match intent (จากตาราง chat_intents)
         -> ดึงคำตอบจริงจากฐานข้อมูล -> log
ไม่เรียก LLM ภายนอก ทำงานออฟไลน์ได้ทั้งหมด
"""
import re
from datetime import datetime

from sqlalchemy.orm import Session

from . import models
from .services import (
    TH_TO_KEY, WEEKDAY_TH, room_status, schedule_to_dict,
    schedules_of_day, weekday_key,
)

MATCH_THRESHOLD = 0.34
THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")


def normalize(text: str) -> str:
    text = text.translate(THAI_DIGITS).lower().strip()
    text = re.sub(r"[?!.,'\"]+", " ", text)
    return re.sub(r"\s+", " ", text)


def extract_entities(db: Session, text: str) -> dict:
    ents = {}
    m = re.search(r"([a-z]{2,4})[\s-]?(\d{3})", text)
    if m:
        ents["room_code"] = f"{m.group(1).upper()}-{m.group(2)}"
        ents["course_code"] = f"{m.group(1).upper()}{m.group(2)}"
    for th, key in TH_TO_KEY.items():
        if th in text:
            ents["weekday"] = key
    if "วันนี้" in text:
        ents["weekday"] = weekday_key(datetime.now().date())
    if "พรุ่งนี้" in text:
        idx = (datetime.now().weekday() + 1) % 7
        ents["weekday"] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][idx]
    for t in db.query(models.Teacher).all():
        short = t.name.replace("อ.", "").replace("ผศ.", "").replace("ดร.", "").strip()
        if short and short.split()[0].lower() in text:
            ents["teacher_id"] = t.teacher_id
    return ents


def match_intent(db: Session, text: str):
    best, best_score = None, 0.0
    intents = (
        db.query(models.ChatIntent)
        .filter(models.ChatIntent.is_active == 1)
        .order_by(models.ChatIntent.priority.desc())
        .all()
    )
    for it in intents:
        kws = [k.strip().lower() for k in it.keywords.split(",") if k.strip()]
        if not kws:
            continue
        hit = sum(1 for k in kws if k in text)
        if hit == 0:
            continue
        score = hit / min(len(kws), 3)
        if score > best_score:
            best, best_score = it, min(score, 1.0)
    return best, round(best_score, 2)


# ---------- handler ของแต่ละ intent ----------

def h_room_status(db, text, ents):
    code = ents.get("room_code")
    q = db.query(models.Room)
    rooms = [q.filter(models.Room.code == code).first()] if code else \
        q.filter(models.Room.type.in_(["lecture", "lab"])).all()
    rooms = [r for r in rooms if r]
    if not rooms:
        return f"ไม่พบห้อง {code} ในระบบครับ", ["ดูแผนผังอาคาร"]
    parts = [f"{r.code} — {room_status(db, r)}" for r in rooms[:6]]
    return "สถานะห้องตอนนี้ (" + datetime.now().strftime("%H:%M") + " น.)\n" + "\n".join(parts), \
        ["ตารางวันนี้", "แผนผังอาคาร"]


def h_teacher_room(db, text, ents):
    tid = ents.get("teacher_id")
    if not tid:
        names = ", ".join(t.name for t in db.query(models.Teacher).limit(8).all())
        return f"ต้องการถามถึงอาจารย์ท่านใดครับ เช่น {names}", []
    t = db.query(models.Teacher).get(tid)
    room = t.room.code if t.room else "ยังไม่ระบุ"
    oh = t.office_hours or "ไม่ได้ระบุเวลาให้คำปรึกษา"
    now_teaching = (
        db.query(models.Schedule)
        .filter(
            models.Schedule.teacher_id == t.teacher_id,
            models.Schedule.weekday == weekday_key(datetime.now().date()),
            models.Schedule.start_time <= datetime.now().time(),
            models.Schedule.end_time >= datetime.now().time(),
        ).first()
    )
    extra = (f"ขณะนี้ติดสอน {now_teaching.course.code} ที่ {now_teaching.room.code} "
             f"ถึง {now_teaching.end_time.strftime('%H:%M')} น.") if now_teaching else \
        "ขณะนี้ไม่มีคาบสอน"
    return f"{t.name} ห้องพัก {room}\nเวลาให้คำปรึกษา: {oh}\n{extra}", ["ดูตารางสอน", "แผนผังอาคาร"]


def h_schedule(db, text, ents):
    day = ents.get("weekday", weekday_key(datetime.now().date()))
    rows = [schedule_to_dict(s) for s in schedules_of_day(db, day)]
    if ents.get("course_code"):
        rows = [r for r in rows if r["course_code"] == ents["course_code"]]
    if ents.get("room_code"):
        rows = [r for r in rows if r["room"] == ents["room_code"]]
    if not rows:
        return f"วัน{WEEKDAY_TH[day]}ไม่มีคาบเรียนตามเงื่อนไขที่ถามครับ", ["ดูทั้งสัปดาห์"]
    lines = [f"{r['start_time']}-{r['end_time']} {r['course_code']} {r['course_name']} "
             f"({r['teacher']}, {r['room']})" for r in rows[:8]]
    return f"ตารางวัน{WEEKDAY_TH[day]}\n" + "\n".join(lines), ["ห้องนี้ว่างไหม", "ถามอาจารย์"]


def h_activity(db, text, ents):
    rows = (
        db.query(models.Activity)
        .filter(models.Activity.start_at >= datetime.now())
        .order_by(models.Activity.start_at).limit(4).all()
    )
    if not rows:
        return "ตอนนี้ยังไม่มีกิจกรรมที่กำลังจะถึงครับ", []
    lines = [f"{a.start_at.strftime('%d/%m %H:%M')} {a.title} ({a.location or 'ไม่ระบุสถานที่'})"
             for a in rows]
    return "กิจกรรมที่กำลังจะถึง\n" + "\n".join(lines), ["เช็คชื่อกิจกรรม"]


HANDLERS = {
    "room_status": h_room_status,
    "teacher_room": h_teacher_room,
    "schedule": h_schedule,
    "activity": h_activity,
}

FALLBACK = (
    "ยังไม่มีข้อมูลสำหรับคำถามนี้ในระบบครับ "
    "ลองถามเรื่องตารางเรียน-สอน ห้องเรียน ห้องอาจารย์ กิจกรรมของสาขา หรือการเช็คชื่อดูนะครับ"
)


def answer(db: Session, question: str, user_type: str = "student") -> dict:
    text = normalize(question)
    ents = extract_entities(db, text)
    intent, score = match_intent(db, text)

    if not intent or score < MATCH_THRESHOLD:
        db.add(models.ChatLog(question=question, intent_name=None, score=score, answered=0))
        db.commit()
        return {"intent": "fallback", "score": score, "answer": FALLBACK,
                "quick_replies": ["ตารางวันนี้", "ห้องอาจารย์", "กิจกรรมของสาขา"]}

    handler = HANDLERS.get(intent.intent_name)
    if handler:
        text_answer, quick = handler(db, text, ents)
    else:
        text_answer, quick = (intent.answer_template or FALLBACK), []

    db.add(models.ChatLog(question=question, intent_name=intent.intent_name,
                          score=score, answered=1))
    db.commit()
    return {"intent": intent.intent_name, "score": score,
            "answer": text_answer, "quick_replies": quick}
