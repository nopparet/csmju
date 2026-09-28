from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    user_type: Optional[str] = "student"


class ChatReply(BaseModel):
    intent: str
    score: float
    answer: str
    quick_replies: List[str] = []


class CheckinRequest(BaseModel):
    code: str                 # รหัสนักศึกษา หรือ payload จาก QR / บัตร
    ref_type: str = "class"   # class | activity
    ref_id: Optional[int] = None
    method: str = "qr"


class CheckinReply(BaseModel):
    ok: bool
    result: str               # present | late | duplicate | denied | not_found | no_session
    message: str
    student_name: Optional[str] = None
    session_title: Optional[str] = None
    checked_count: Optional[int] = None


class VisitLogIn(BaseModel):
    user_type: str
    module: Optional[str] = None
    duration_sec: int = 0
