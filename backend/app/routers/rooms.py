from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..services import room_status

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("")
def list_rooms(q: str | None = None, floor: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Room)
    if q:
        query = query.filter(models.Room.code.like(f"%{q}%") | models.Room.name.like(f"%{q}%"))
    if floor:
        query = query.filter(models.Room.floor == floor)
    rooms = query.order_by(models.Room.floor, models.Room.code).all()
    return [
        {
            "room_id": r.room_id, "code": r.code, "name": r.name, "type": r.type,
            "floor": r.floor, "pos_x": r.pos_x, "pos_y": r.pos_y, "hint": r.hint,
            "status": room_status(db, r),
            "owner": next((t.name for t in db.query(models.Teacher)
                           .filter(models.Teacher.room_id == r.room_id)), None),
        }
        for r in rooms
    ]


@router.get("/teachers")
def list_teachers(db: Session = Depends(get_db)):
    return [
        {
            "teacher_id": t.teacher_id, "name": t.name, "email": t.email,
            "office_hours": t.office_hours, "room": t.room.code if t.room else None,
        }
        for t in db.query(models.Teacher).order_by(models.Teacher.name).all()
    ]
