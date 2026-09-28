from sqlalchemy import (
    Column, Integer, SmallInteger, String, Text, Date, Time, DateTime,
    Enum, Float, ForeignKey, UniqueConstraint, func,
)
from sqlalchemy.orm import relationship

from .database import Base


class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)      # CS-201
    name = Column(String(100))                                  # ห้องบรรยาย 60 ที่นั่ง
    type = Column(Enum("lecture", "lab", "office", "meeting", "service"), default="lecture")
    floor = Column(SmallInteger, default=1)
    pos_x = Column(SmallInteger, default=0)   # พิกัดบนแผนผัง (viewBox ของ SVG)
    pos_y = Column(SmallInteger, default=0)
    hint = Column(String(255))                # คำบอกทางสั้น ๆ


class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120))
    phone = Column(String(30))
    office_hours = Column(String(120))
    room_id = Column(Integer, ForeignKey("rooms.room_id"))
    room = relationship("Room")


class Student(Base):
    __tablename__ = "students"
    student_id = Column(String(15), primary_key=True)
    name = Column(String(100), nullable=False)
    year_level = Column(SmallInteger)
    program = Column(String(80))
    card_uid = Column(String(50), unique=True)   # UID จากบัตรนักศึกษา


class Course(Base):
    __tablename__ = "courses"
    course_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)   # CS202
    name = Column(String(150), nullable=False)
    credit = Column(SmallInteger, default=3)
    year_level = Column(SmallInteger)


class Schedule(Base):
    """ตารางประจำสัปดาห์ (แม่แบบ)"""
    __tablename__ = "schedules"
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    room_id = Column(Integer, ForeignKey("rooms.room_id"))
    weekday = Column(Enum("mon", "tue", "wed", "thu", "fri", "sat", "sun"), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    term = Column(String(10), default="1/2568")

    course = relationship("Course")
    teacher = relationship("Teacher")
    room = relationship("Room")


class ClassSession(Base):
    """คาบจริงรายวันที่ — ใช้ผูกกับการเช็คชื่อ"""
    __tablename__ = "class_sessions"
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedules.schedule_id"), nullable=False)
    session_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(Enum("open", "closed", "cancelled"), default="open")
    __table_args__ = (UniqueConstraint("schedule_id", "session_date", name="uq_sched_date"),)

    schedule = relationship("Schedule")


class Enrollment(Base):
    __tablename__ = "enrollments"
    enroll_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    student_id = Column(String(15), ForeignKey("students.student_id"), nullable=False)
    __table_args__ = (UniqueConstraint("course_id", "student_id", name="uq_enroll"),)


class Activity(Base):
    __tablename__ = "activities"
    activity_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    detail = Column(Text)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime)
    location = Column(String(100))
    is_checkin_open = Column(SmallInteger, default=0)


class Attendance(Base):
    __tablename__ = "attendance"
    att_id = Column(Integer, primary_key=True, autoincrement=True)
    ref_type = Column(Enum("class", "activity"), nullable=False)
    ref_id = Column(Integer, nullable=False)
    student_id = Column(String(15), ForeignKey("students.student_id"), nullable=False)
    checked_at = Column(DateTime, server_default=func.now())
    method = Column(Enum("qr", "card", "manual"), default="qr")
    result = Column(Enum("present", "late", "denied"), default="present")
    __table_args__ = (UniqueConstraint("ref_type", "ref_id", "student_id", name="uq_once"),)


class VisitLog(Base):
    __tablename__ = "visit_logs"
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_type = Column(Enum("student", "teacher", "visitor"), nullable=False)
    module = Column(String(40))
    started_at = Column(DateTime, server_default=func.now())
    duration_sec = Column(Integer, default=0)


class ChatIntent(Base):
    __tablename__ = "chat_intents"
    intent_id = Column(Integer, primary_key=True, autoincrement=True)
    intent_name = Column(String(50), unique=True, nullable=False)
    keywords = Column(Text, nullable=False)     # คั่นด้วย comma
    answer_template = Column(Text)              # ใช้เมื่อ intent นั้นไม่มี handler เฉพาะ
    priority = Column(SmallInteger, default=5)
    is_active = Column(SmallInteger, default=1)


class ChatLog(Base):
    __tablename__ = "chat_logs"
    chat_id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    intent_name = Column(String(50))
    score = Column(Float, default=0)
    answered = Column(SmallInteger, default=1)
    asked_at = Column(DateTime, server_default=func.now())
