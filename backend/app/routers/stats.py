from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import VisitLogIn

router = APIRouter(prefix="/api", tags=["stats"])


@router.post("/logs/visit")
def log_visit(item: VisitLogIn, db: Session = Depends(get_db)):
    db.add(models.VisitLog(user_type=item.user_type, module=item.module,
                           duration_sec=item.duration_sec))
    db.commit()
    return {"ok": True}


@router.get("/stats")
def stats(days: int = 7, db: Session = Depends(get_db)):
    since = datetime.now() - timedelta(days=days)

    by_day = (db.query(func.date(models.VisitLog.started_at).label("d"),
                       func.count().label("c"))
              .filter(models.VisitLog.started_at >= since)
              .group_by("d").order_by("d").all())
    by_type = (db.query(models.VisitLog.user_type, func.count())
               .filter(models.VisitLog.started_at >= since)
               .group_by(models.VisitLog.user_type).all())
    by_module = (db.query(models.VisitLog.module, func.count())
                 .filter(models.VisitLog.started_at >= since)
                 .group_by(models.VisitLog.module)
                 .order_by(func.count().desc()).limit(6).all())
    total_chat = db.query(models.ChatLog).filter(models.ChatLog.asked_at >= since).count()
    answered = (db.query(models.ChatLog)
                .filter(models.ChatLog.asked_at >= since,
                        models.ChatLog.answered == 1).count())
    top_intents = (db.query(models.ChatLog.intent_name, func.count())
                   .filter(models.ChatLog.asked_at >= since,
                           models.ChatLog.answered == 1)
                   .group_by(models.ChatLog.intent_name)
                   .order_by(func.count().desc()).limit(5).all())
    unanswered = (db.query(models.ChatLog.question)
                  .filter(models.ChatLog.answered == 0)
                  .order_by(models.ChatLog.asked_at.desc()).limit(10).all())

    return {
        "range_days": days,
        "total_visits": sum(c for _, c in by_day),
        "by_day": [{"date": str(d), "count": c} for d, c in by_day],
        "by_type": [{"type": t, "count": c} for t, c in by_type],
        "by_module": [{"module": m or "-", "count": c} for m, c in by_module],
        "chat": {
            "total": total_chat,
            "answered": answered,
            "coverage": round(answered / total_chat * 100, 1) if total_chat else 0,
            "top_intents": [{"intent": i or "-", "count": c} for i, c in top_intents],
            "unanswered_samples": [q for (q,) in unanswered],
        },
    }
