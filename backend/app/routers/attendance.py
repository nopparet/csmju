import re
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..config import CHECKIN_EARLY_MIN, CHECKIN_LATE_MIN
from ..database import get_db
from ..schemas import CheckinReply, CheckinRequest
from ..services import current_session

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.post("/student")
def register_student(data: dict, db: Session = Depends(get_db)):
    """เพิ่มนักศึกษาเข้าระบบด้วยรหัส+ชื่อ ไม่ต้องมีข้อมูล enrollment"""
    sid = str(data.get("student_id", "")).strip()
    name = str(data.get("name", "")).strip()
    if not sid or not name:
        return {"ok": False, "message": "ต้องระบุ student_id และ name"}
    exist = db.query(models.Student).get(sid)
    if exist:
        return {"ok": True, "message": f"มีในระบบแล้ว: {exist.name}", "student_id": sid}
    st = models.Student(student_id=sid, name=name,
                        year_level=int(str(sid)[2]) if len(sid) >= 3 else 1,
                        program="วิทยาการคอมพิวเตอร์")
    db.add(st)
    db.commit()
    return {"ok": True, "message": f"เพิ่ม {name} เรียบร้อย", "student_id": sid}


def resolve_student(db: Session, code: str):
    """รับได้ทั้งรหัสนักศึกษา, UID บัตร และ payload แบบ STU:6712345678"""
    code = code.strip()
    m = re.search(r"(\d{8,15})", code)
    if m:
        st = db.query(models.Student).get(m.group(1))
        if st:
            return st
    return db.query(models.Student).filter(models.Student.card_uid == code).first()


@router.get("/current")
def current(db: Session = Depends(get_db)):
    """คาบที่เปิดให้เช็คชื่อตอนนี้ — หน้าจอใช้แสดงหัวข้อและสร้าง QR"""
    sess, _ = current_session(db, CHECKIN_EARLY_MIN, CHECKIN_LATE_MIN)
    if not sess:
        return {"open": False}
    s = sess.schedule
    count = (db.query(models.Attendance)
             .filter_by(ref_type="class", ref_id=sess.session_id).count())
    return {
        "open": True, "session_id": sess.session_id,
        "title": f"{s.course.code} {s.course.name}",
        "room": s.room.code if s.room else "-",
        "time": f"{sess.start_time.strftime('%H:%M')}-{sess.end_time.strftime('%H:%M')}",
        "checked_count": count,
        "qr_payload": f"KIOSK:CLASS:{sess.session_id}",
    }


@router.post("", response_model=CheckinReply)
def checkin(req: CheckinRequest, db: Session = Depends(get_db)):
    student = resolve_student(db, req.code)
    if not student:
        return CheckinReply(ok=False, result="not_found",
                            message="ไม่พบรหัสนี้ในระบบ กรุณาติดต่อสำนักงานสาขา")

    if req.ref_type == "class":
        sess, on_time = current_session(db, CHECKIN_EARLY_MIN, CHECKIN_LATE_MIN)
        if not sess:
            return CheckinReply(ok=False, result="no_session",
                                message="ขณะนี้ยังไม่มีคาบที่เปิดให้เช็คชื่อ")
        ref_id, title = sess.session_id, f"{sess.schedule.course.code} {sess.schedule.course.name}"
        result = on_time
    else:
        act = db.query(models.Activity).get(req.ref_id)
        if not act or not act.is_checkin_open:
            return CheckinReply(ok=False, result="no_session",
                                message="กิจกรรมนี้ยังไม่เปิดให้เช็คชื่อ")
        ref_id, title, result = act.activity_id, act.title, "present"

    dup = (db.query(models.Attendance)
           .filter_by(ref_type=req.ref_type, ref_id=ref_id,
                      student_id=student.student_id).first())
    if dup:
        return CheckinReply(ok=False, result="duplicate", student_name=student.name,
                            session_title=title,
                            message=f"เช็คชื่อไปแล้วเมื่อ {dup.checked_at.strftime('%H:%M')} น.")

    db.add(models.Attendance(ref_type=req.ref_type, ref_id=ref_id,
                             student_id=student.student_id,
                             method=req.method, result=result))
    db.commit()
    count = (db.query(models.Attendance)
             .filter_by(ref_type=req.ref_type, ref_id=ref_id, result=result).count())
    label = "มาเรียน (ตรงเวลา)" if result == "present" else "มาสาย"
    return CheckinReply(ok=True, result=result, student_name=student.name,
                        session_title=title, checked_count=count,
                        message=f"เช็คชื่อสำเร็จ · {label} · {datetime.now().strftime('%H:%M')} น.")
