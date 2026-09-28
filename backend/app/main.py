from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .routers import attendance, chat, rooms, schedule, stats
from .services import ensure_sessions_for_today


@asynccontextmanager
async def lifespan(app: FastAPI):
    # สร้างตารางที่ยังไม่มี และเตรียมคาบเรียนของวันนี้
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_sessions_for_today(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Smart Reception Kiosk API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # dev
        "http://localhost:4173",   # vite preview
        "http://localhost",        # nginx บน Pi (port 80)
        "http://localhost:80",
        "http://127.0.0.1",
        "http://127.0.0.1:80",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (rooms.router, schedule.router, chat.router, attendance.router, stats.router):
    app.include_router(r)


@app.get("/api/health")
def health():
    return {"status": "ok"}
