from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import chatbot
from ..database import get_db
from ..schemas import ChatReply, ChatRequest

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatReply)
def ask(req: ChatRequest, db: Session = Depends(get_db)):
    return chatbot.answer(db, req.question, req.user_type)
