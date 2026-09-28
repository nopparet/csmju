"""ฟังก์ชันที่ใช้ร่วมกันหลายโมดูล"""
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from . import models

WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
WEEKDAY_TH = {"mon": "จันทร์", "tue": "อังคาร", "wed": "พุธ", "thu": "พฤหัสบดี",
              "fri": "ศุกร์", "sat": "เสาร์", "sun": "อาทิตย์"}
TH_TO_KEY = {v: k for k, v in WEEKDAY_TH.items()}


def weekday_key(d: date) -> str:
    return WEEKDAY_KEYS[d.weekday()]


def schedules_of_day(db: Session, day: str):
    return (
        db.query(models.Schedule)
        .filter(models.Schedule.weekday == day)
        .order_by(models.Schedule.start_time)
        .all()
    )


def schedule_to_dict(s: models.Schedule, now: datetime | None = None) -> dict:
    now = now or datetime.now()
    is_now = (
        weekday_key(now.date()) == s.weekday
        and s.start_time <= now.time() <= s.end_time
    )
    return {
        "schedule_id": s.schedule_id,
        "weekday": s.weekday,
        "weekday_th": WEEKDAY_TH.get(s.weekday, s.weekday),
        "start_time": s.start_time.strftime("%H:%M"),
        "end_time": s.end_time.strftime("%H:%M"),
        "course_code": s.course.code if s.course else None,
        "course_name": s.course.name if s.course else None,
        "year_level": s.course.year_level if s.course else None,
        "teacher": s.teacher.name if s.teacher else "-",
        "room": s.room.code if s.room else "-",
        "is_now": is_now,
    }


def room_status(db: Session, room: models.Room, now: datetime | None = None) -> str:
    """ห้องนี้กำลังถูกใช้อยู่หรือไม่ ณ เวลานี้"""
    now = now or datetime.now()
    s = (
        db.query(models.Schedule)
        .filter(
            models.Schedule.room_id == room.room_id,
            models.Schedule.weekday == weekday_key(now.date()),
            models.Schedule.start_time <= now.time(),
            models.Schedule.end_time >= now.time(),
        )
        .first()
    )
    if not s:
        return "ว่าง"
    return f"ใช้งานอยู่ · {s.course.code if s.course else ''} ถึง {s.end_time.strftime('%H:%M')}"


def current_session(db: Session, early_min: int, late_min: int):
    """หาคาบที่เปิดให้เช็คชื่อได้ ณ ตอนนี้"""
    now = datetime.now()
    rows = (
        db.query(models.ClassSession)
        .filter(
            models.ClassSession.session_date == now.date(),
            models.ClassSession.status == "open",
        )
        .all()
    )
    for row in rows:
        start = datetime.combine(row.session_date, row.start_time)
        if start - timedelta(minutes=early_min) <= now <= start + timedelta(minutes=late_min):
            return row, "present" if now <= start + timedelta(minutes=10) else "late"
    return None, None


def ensure_sessions_for_today(db: Session):
    """สร้าง class_sessions ของวันนี้จากตารางประจำสัปดาห์ (เรียกตอนเปิดเครื่อง หรือ cron)"""
    today = date.today()
    day = weekday_key(today)
    created = 0
    for s in schedules_of_day(db, day):
        exists = (
            db.query(models.ClassSession)
            .filter_by(schedule_id=s.schedule_id, session_date=today)
            .first()
        )
        if not exists:
            db.add(models.ClassSession(
                schedule_id=s.schedule_id, session_date=today,
                start_time=s.start_time, end_time=s.end_time, status="open",
            ))
            created += 1
    db.commit()
    return created
