from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..services import schedule_to_dict, schedules_of_day, weekday_key

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.get("")
def get_schedule(
    day: str | None = None,
    room: str | None = None,
    teacher_id: int | None = None,
    year_level: int | None = None,
    db: Session = Depends(get_db),
):
    day = day or weekday_key(datetime.now().date())
    rows = [schedule_to_dict(s) for s in schedules_of_day(db, day)]
    if room:
        rows = [r for r in rows if r["room"] == room]
    if year_level:
        rows = [r for r in rows if r["year_level"] == year_level]
    if teacher_id:
        ids = {s.schedule_id for s in db.query(models.Schedule)
               .filter(models.Schedule.teacher_id == teacher_id)}
        rows = [r for r in rows if r["schedule_id"] in ids]
    return {"day": day, "items": rows}


@router.get("/activities")
def activities(db: Session = Depends(get_db)):
    rows = (db.query(models.Activity)
            .filter(models.Activity.start_at >= datetime.now())
            .order_by(models.Activity.start_at).limit(10).all())
    return [
        {"activity_id": a.activity_id, "title": a.title, "detail": a.detail,
         "start_at": a.start_at.isoformat(), "location": a.location,
         "checkin_open": bool(a.is_checkin_open)}
        for a in rows
    ]
