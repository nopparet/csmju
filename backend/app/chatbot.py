"""
Chatbot แบบ rule-based (ปรับปรุงใหม่)
- keyword matching ฉลาดขึ้น: ใช้ token overlap แทน exact substring
- entity extraction: ชื่ออาจารย์แบบ fuzzy, ชื่อห้อง, ชื่อวิชา
- handler ใหม่: navigate, course_info, greeting_smart
- fallback ฉลาดขึ้น: บอก intent ที่ใกล้เคียง
"""
import re
from datetime import datetime

from sqlalchemy.orm import Session

from . import models
from .gemini_chat import ask_gemini
from .services import (
    TH_TO_KEY, WEEKDAY_TH, room_status, schedule_to_dict,
    schedules_of_day, weekday_key,
)

MATCH_THRESHOLD = 0.25
THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")

# คำที่ไม่มีความหมาย (stop words)
STOP_WORDS = {"ที่","ไหน","อยู่","อยาก","ต้องการ","ไป","หา","ขอ","ดู","บอก","แจ้ง",
              "ช่วย","หน่อย","ได้","ไหม","มั้ย","มาก","นะ","ครับ","ค่ะ","คะ","นะครับ",
              "นะคะ","เลย","ด้วย","ให้","เกี่ยว","กับ","คือ","เป็น","และ","หรือ"}

ROOM_ALIASES = {
    "ห้องพักอาจารย์": "OFFICE",
    "ออฟฟิศ": "OFFICE",
    "ห้องอาจารย์": "OFFICE",
    "ห้องประชุม": "MEET",
    "ห้องเก็บของ": "STORE",
    "ห้องเก็บอุปกรณ์": "STORE",
    "เน็ต": "NET",
    "เครือข่าย": "NET",
    "network": "NET",
    "lab1": "LAB-1", "lab2": "LAB-2", "lab3": "LAB-3",
    "lab4": "LAB-4", "lab5": "LAB-5",
    "labcom1": "LAB-1", "labcom2": "LAB-2", "labcom3": "LAB-3",
    "labcom4": "LAB-4", "labcom5": "LAB-5",
    "lect6": "LECT-6", "lect8": "LECT-8",
    "บรรยาย6": "LECT-6", "บรรยาย8": "LECT-8",
}

ROOM_DIRECTIONS = {
    "OFFICE": "ห้องพักอาจารย์อยู่ซ้ายสุดของชั้น 6 ข้างๆ บันไดหนีไฟครับ",
    "LAB-1":  "LAB-1 อยู่ฝั่งซ้าย บน-ซ้าย ของบล็อกห้อง Lab ครับ",
    "LAB-2":  "LAB-2 อยู่ฝั่งซ้าย ล่าง-ซ้าย ของบล็อกห้อง Lab ครับ",
    "LAB-3":  "LAB-3 อยู่ฝั่งซ้าย ล่าง-ขวา ของบล็อกห้อง Lab ครับ",
    "LAB-4":  "LAB-4 อยู่ฝั่งซ้าย บน-ขวา ของบล็อกห้อง Lab ครับ",
    "LAB-5":  "LAB-5 อยู่บล็อกกลาง ด้านล่าง ถัดจากห้องเก็บอุปกรณ์ครับ",
    "NET":    "ห้องปฏิบัติการเครือข่ายฯ (NET) อยู่บล็อกกลาง ด้านบนสุดครับ",
    "STORE":  "ห้องเก็บอุปกรณ์สาขาอยู่บล็อกกลาง ระหว่าง NET กับ LAB-5 ครับ",
    "LECT-8": "ห้องบรรยายคอม 8 อยู่บล็อกขวา ด้านบนสุดครับ",
    "MEET":   "ห้องประชุมสาขาอยู่บล็อกขวา กลาง ระหว่าง LECT-8 กับ LECT-6 ครับ",
    "LECT-6": "ห้องบรรยายคอม 6 อยู่บล็อกขวา ด้านล่างสุดครับ",
}


def normalize(text: str) -> str:
    text = text.translate(THAI_DIGITS).lower().strip()
    text = re.sub(r"[?!.,'\"\(\)]+", " ", text)
    return re.sub(r"\s+", " ", text)


def tokenize(text: str) -> set:
    """แบ่งคำและกรอง stop words"""
    tokens = set(text.split())
    return tokens - STOP_WORDS


def extract_entities(db: Session, text: str) -> dict:
    ents = {}

    # --- room code จาก pattern เช่น lab-2, lect-6 ---
    m = re.search(r"(lab|lect|net|meet|store|office)[- ]?(\d+)?", text)
    if m:
        code = m.group(1).upper()
        num = m.group(2) or ""
        ents["room_code"] = f"{code}-{num}" if num else code

    # --- room alias (ชื่อเต็ม) ---
    for alias, code in ROOM_ALIASES.items():
        if alias in text:
            ents["room_code"] = code
            break

    # --- course code ---
    mc = re.search(r"\b(103\d{5})\b", text)
    if mc:
        ents["course_code"] = mc.group(1)

    # --- วัน ---
    for th, key in TH_TO_KEY.items():
        if th in text:
            ents["weekday"] = key
    if "วันนี้" in text:
        ents["weekday"] = weekday_key(datetime.now().date())
    if "พรุ่งนี้" in text:
        idx = (datetime.now().weekday() + 1) % 7
        ents["weekday"] = ["mon","tue","wed","thu","fri","sat","sun"][idx]

    # --- ชื่ออาจารย์ (fuzzy: ตัดคำนำหน้าออก, จับชื่อแรก) ---
    for t in db.query(models.Teacher).all():
        clean = re.sub(r"(ผศ|อ|ดร|นางสาว|นาย|นาง)\.", "", t.name).strip()
        parts = clean.split()
        # ตรวจทั้งชื่อแรกและนามสกุล
        for p in parts:
            if len(p) >= 3 and p.lower() in text:
                ents["teacher_id"] = t.teacher_id
                break

    # --- student_id: ตัวเลข 8-12 หลัก ที่ไม่ใช่ course code ---
    ms = re.search(r'\b(\d{8,12})\b', text)
    if ms and not mc:  # ไม่ใช่ course code
        ents['student_id_raw'] = ms.group(1)

    return ents


def match_intent(db: Session, text: str):
    """Improved matching: token-based overlap + partial match"""
    best, best_score = None, 0.0
    tokens = tokenize(text)

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

        # วิธีที่ 1: exact substring match (เดิม)
        hit_exact = sum(1 for k in kws if k in text)

        # วิธีที่ 2: token overlap (คำแต่ละคำใน keyword ที่อยู่ใน tokens)
        hit_token = sum(1 for k in kws if k in tokens)

        hit = max(hit_exact, hit_token)
        if hit == 0:
            continue

        score = hit / min(len(kws), 4)
        if score > best_score:
            best, best_score = it, min(score, 1.0)

    return best, round(best_score, 2)


# ─────────────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────────────

def h_room_status(db, text, ents):
    code = ents.get("room_code")
    q = db.query(models.Room)
    if code:
        rooms = [q.filter(models.Room.code == code).first()]
    else:
        rooms = q.filter(models.Room.type.in_(["lecture","lab"])).order_by(models.Room.code).all()
    rooms = [r for r in rooms if r]
    if not rooms:
        return f"ไม่พบห้อง '{code}' ในระบบครับ", ["ดูแผนผังอาคาร"]
    parts = [f"🔲 {r.code} — {room_status(db, r)}" for r in rooms[:8]]
    return "สถานะห้องตอนนี้ (" + datetime.now().strftime("%H:%M") + " น.)\n" + "\n".join(parts), \
        ["ตารางวันนี้", "แผนผังอาคาร"]


def h_navigate(db, text, ents):
    """บอกทิศทางไปห้องต่างๆ"""
    code = ents.get("room_code")
    if code:
        direction = ROOM_DIRECTIONS.get(code)
        if direction:
            r = db.query(models.Room).filter(models.Room.code == code).first()
            name = r.name if r else code
            status = room_status(db, r) if r else ""
            return f"📍 {name} ({code})\n{direction}\nสถานะ: {status}", ["แผนผังอาคาร"]
        return f"ไม่มีข้อมูลทิศทางสำหรับห้อง {code} ครับ", ["แผนผังอาคาร"]

    # ไม่ระบุห้อง — แสดงรายการห้องทั้งหมด
    lines = [f"• {code}: {d[:40]}" for code, d in ROOM_DIRECTIONS.items()]
    return "ห้องในชั้น 6 ที่สามารถนำทางได้:\n" + "\n".join(lines), ["แผนผังอาคาร"]


def h_teacher_room(db, text, ents):
    tid = ents.get("teacher_id")
    if not tid:
        # ถ้าไม่ระบุอาจารย์ แต่ถามถึงห้องพักอาจารย์โดยรวม
        if any(w in text for w in ["ห้องพักอาจารย์", "ห้องอาจารย์", "office"]):
            teachers = db.query(models.Teacher).filter(
                models.Teacher.email != 'chorthip.s@mju.ac.th').all()
            names = ", ".join(t.name.split()[-2] if len(t.name.split()) >= 2
                             else t.name for t in teachers[:5])
            return (f"📍 ห้องพักอาจารย์อยู่ซ้ายสุดของชั้น 6 ครับ\n"
                    f"เปิดทำการ จ–ศ 08:30–16:30 น.\n"
                    f"อาจารย์ในสาขา: {names} และอีก {len(teachers)-5} ท่าน"), \
                   ["แผนผังอาคาร", "ตารางสอนอาจารย์"]
        names_list = "\n".join(f"• {t.name}" for t in db.query(models.Teacher)
                               .filter(models.Teacher.email != 'chorthip.s@mju.ac.th').all())
        return f"อาจารย์ประจำสาขาวิทยาการคอมพิวเตอร์:\n{names_list}\n\nพิมพ์ชื่ออาจารย์เพื่อดูตารางสอนและเวลาให้คำปรึกษาครับ", []

    t = db.query(models.Teacher).get(tid)
    room = t.room.name if t.room else "ยังไม่ระบุ"
    oh = t.office_hours or "ไม่ได้ระบุเวลาให้คำปรึกษา"
    phone = t.phone or "-"
    now_teaching = (
        db.query(models.Schedule)
        .filter(
            models.Schedule.teacher_id == t.teacher_id,
            models.Schedule.weekday == weekday_key(datetime.now().date()),
            models.Schedule.start_time <= datetime.now().time(),
            models.Schedule.end_time >= datetime.now().time(),
        ).first()
    )
    if now_teaching:
        extra = (f"⚠️ ขณะนี้ติดสอน {now_teaching.course.code} "
                 f"ที่ {now_teaching.room.code} ถึง {now_teaching.end_time.strftime('%H:%M')} น.")
    else:
        extra = "✅ ขณะนี้ไม่มีคาบสอน อาจอยู่ที่ห้องพักอาจารย์"
    return (f"👨‍🏫 {t.name}\n"
            f"📍 ห้องพัก: {room}\n"
            f"🕐 เวลาให้คำปรึกษา: {oh}\n"
            f"📞 โทร: {phone}\n"
            f"{extra}"), ["แผนผังอาคาร", "ตารางสอนวันนี้"]


def h_schedule(db, text, ents):
    day = ents.get("weekday", weekday_key(datetime.now().date()))
    rows = [schedule_to_dict(s) for s in schedules_of_day(db, day)]

    # กรองตาม teacher_id ถ้าถามเรื่องอาจารย์คนใดคนหนึ่ง
    tid = ents.get("teacher_id")
    if tid:
        t = db.query(models.Teacher).get(tid)
        t_name = t.name if t else ""
        rows = [r for r in rows if r.get("teacher") == t_name]

    if ents.get("course_code"):
        rows = [r for r in rows if r["course_code"] == ents["course_code"]]
    if ents.get("room_code"):
        rows = [r for r in rows if r["room"] == ents["room_code"]]

    if not rows:
        day_label = WEEKDAY_TH.get(day, day)
        return f"วัน{day_label}ไม่มีคาบเรียนตามเงื่อนไขที่ถามครับ", \
               [f"ตารางวัน{WEEKDAY_TH.get('mon','จันทร์')}", "ดูทั้งสัปดาห์"]

    now = datetime.now().time()
    lines = []
    for r in rows[:10]:
        is_now = (r["start_time"] <= now.strftime("%H:%M") <= r["end_time"]
                  if ents.get("weekday") == weekday_key(datetime.now().date()) else False)
        marker = "▶️ " if is_now else "   "
        lines.append(f"{marker}{r['start_time']}-{r['end_time']} "
                     f"{r['course_code']} {r['course_name']} ({r['room']})")

    return f"📅 ตารางวัน{WEEKDAY_TH.get(day, day)}\n" + "\n".join(lines), \
           ["ห้องนี้ว่างไหม", "ถามอาจารย์"]


def h_activity(db, text, ents):
    rows = (
        db.query(models.Activity)
        .filter(models.Activity.start_at >= datetime.now())
        .order_by(models.Activity.start_at).limit(4).all()
    )
    if not rows:
        return "ตอนนี้ยังไม่มีกิจกรรมที่กำลังจะถึงครับ", []
    lines = [f"📌 {a.start_at.strftime('%d/%m %H:%M')} — {a.title} "
             f"({a.location or 'ไม่ระบุสถานที่'})" for a in rows]
    return "กิจกรรมที่กำลังจะถึง\n" + "\n".join(lines), ["เช็คชื่อกิจกรรม"]


def h_student(db, text, ents):
    m = re.search(r"\d{8,10}", text)
    if m:
        sid = m.group(0)
        st = db.query(models.Student).get(sid)
        if st:
            return (f"🎓 รหัส {st.student_id}\n"
                    f"ชื่อ {st.name}\n"
                    f"ชั้นปีที่ {st.year_level} · สาขา{st.program}"), []
        return f"ไม่พบรหัสนักศึกษา {sid} ในระบบครับ", ["ติดต่อสำนักงาน"]

    name_text = re.sub(r"(นาย|นางสาว|นาง|ค้นหา|หา|นักศึกษา|ชื่อ)", "", text).strip()
    if len(name_text) >= 2:
        students = (db.query(models.Student)
                    .filter(models.Student.name.like(f"%{name_text}%"))
                    .limit(5).all())
        if students:
            lines = [f"• {s.student_id}  {s.name}  (ปี {s.year_level})" for s in students]
            return f"ผลการค้นหา \"{name_text}\"\n" + "\n".join(lines), []
        return f"ไม่พบนักศึกษาที่ชื่อ \"{name_text}\" ในระบบครับ", ["ติดต่อสำนักงาน"]

    total = db.query(models.Student).count()
    return (f"มีนักศึกษาในระบบทั้งหมด {total} คน (ปีการศึกษา 2566)\n"
            f"พิมพ์ชื่อหรือรหัสนักศึกษาเพื่อค้นหาครับ"), []


def h_contact(db, text, ents):
    return ("📞 ติดต่อสาขาวิทยาการคอมพิวเตอร์\n"
            "🏢 อาคารแม่โจ้ 60 ปี ชั้น 6\n"
            "📱 053-873800 (ชั้น 6)\n"
            "🌐 csmju.com\n"
            "⏰ เปิดทำการ จ–ศ 08:30–16:30 น."), ["แผนผังอาคาร", "ห้องอาจารย์"]


HANDLERS = {
    "room_status": h_room_status,
    "navigate":    h_navigate,
    "teacher_room": h_teacher_room,
    "schedule":    h_schedule,
    "activity":    h_activity,
    "student":     h_student,
    "contact":     h_contact,
}

FALLBACK = (
    "ขออภัยครับ ยังไม่เข้าใจคำถามนี้ 😅\n"
    "ลองถามเกี่ยวกับ:\n"
    "• ตารางเรียน-สอน ('ตารางวันนี้', 'วันจันทร์มีอะไร')\n"
    "• ห้องเรียน ('LAB-2 ว่างไหม', 'ห้องบรรยาย')\n"
    "• อาจารย์ ('อ.สนิท อยู่ที่ไหน', 'อ.ปวีณ สอนอะไร')\n"
    "• ค้นหานักศึกษา ('หา กรรชัย', 'รหัส 6604101301')\n"
    "• ติดต่อสาขา"
)


def answer(db: Session, question: str, user_type: str = "student") -> dict:
    text = normalize(question)
    ents = extract_entities(db, text)
    intent, score = match_intent(db, text)

    # smart fallback: ถ้าจับ entity ได้แต่ intent ต่ำ ให้ใช้ entity นำทาง
    if (not intent or score < MATCH_THRESHOLD) and ents.get("room_code"):
        intent_name = "navigate"
        text_answer, quick = h_navigate(db, text, ents)
        db.add(models.ChatLog(question=question, intent_name=intent_name, score=score, answered=1))
        db.commit()
        return {"intent": intent_name, "score": score, "answer": text_answer, "quick_replies": quick}

    if (not intent or score < MATCH_THRESHOLD) and ents.get("teacher_id"):
        text_answer, quick = h_teacher_room(db, text, ents)
        db.add(models.ChatLog(question=question, intent_name="teacher_room", score=score, answered=1))
        db.commit()
        return {"intent": "teacher_room", "score": score, "answer": text_answer, "quick_replies": quick}

    if (not intent or score < MATCH_THRESHOLD) and ents.get("student_id_raw"):
        text_answer, quick = h_student(db, text, ents)
        db.add(models.ChatLog(question=question, intent_name="student", score=score, answered=1))
        db.commit()
        return {"intent": "student", "score": score, "answer": text_answer, "quick_replies": quick}

    if not intent or score < MATCH_THRESHOLD:
        # ลอง Gemini ก่อน fallback
        gemini_ans = ask_gemini(db, question)
        if gemini_ans:
            db.add(models.ChatLog(question=question, intent_name="gemini", score=score, answered=1))
            db.commit()
            return {"intent": "gemini", "score": score, "answer": gemini_ans,
                    "quick_replies": ["ตารางวันนี้", "ห้องอาจารย์", "ติดต่อสาขา"]}
        db.add(models.ChatLog(question=question, intent_name=None, score=score, answered=0))
        db.commit()
        return {"intent": "fallback", "score": score, "answer": FALLBACK,
                "quick_replies": ["ตารางวันนี้", "ห้องอาจารย์", "กิจกรรมของสาขา", "ติดต่อสาขา"]}

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
