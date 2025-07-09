from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from MySql.database import get_db
from MySql.models import User
from pydantic import BaseModel
from typing import List
import os
import openai
from datetime import datetime
# from .utils import analyze_emotion, summarize_text, generate_image
# from .chat import get_chat_history
# from .diary_db import get_diary_entries, save_diary_entry
#
router = APIRouter()
#
# openai.api_key = os.getenv("OPENAI_API_KEY")
#
# class DiaryResponse(BaseModel):
#     title: str
#     content: str
#     emotion: str
#     summary: str
#     image_url: str
#
# class DiaryEntry(BaseModel):
#     pk: str
#     id: str
#     userId: str
#     date: datetime
#     title: str
#     content: str
#     emotion: str
#     summary: str
#     image_url: str
#
# @router.get("/diary/entries", response_model=List[DiaryEntry])
# async def fetch_diary_entries(pk: str = Query(...)):
#     entries = get_diary_entries(pk)
#     return entries
#
# @router.get("/diary", response_model=DiaryResponse)
# async def generate_diary(pk: str = Query(...)):
#     chat_history = get_chat_history(pk)
#     combined_text = " ".join([msg["content"] for msg in chat_history if msg["role"] == "user"])
#
#     emotion = analyze_emotion(combined_text)
#     summary = summarize_text(combined_text)
#     content = f"{summary} 상담을 통해 내 마음을 더 잘 이해하게 되었다."
#     title = {
#         "happy": "밝은 하루", "sad": "생각이 많은 날", "neutral": "평범한 일상",
#         "excited": "설레는 순간", "anxious": "복잡한 하루"
#     }.get(emotion, "감정의 기록")
#     image_url = generate_image(emotion)
#
#     save_diary_entry(pk, title, content, emotion, summary, image_url)
#
#     return DiaryResponse(
#         title=title,
#         content=content,
#         emotion=emotion,
#         summary=summary,
#         image_url=image_url
#     )
@router.get("/users/diary")
def get_diary(pk: int = Query(...), db: Session = Depends(get_db)):
    # 유저 정보 확인
    user = db.query(User).filter(User.pk == pk).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "title": "오늘의 너",
        "content": "오늘 너와 나눈 대화는 따뜻했어.",
        "emotion": "happy",
        "image_url": "/default-image.png",
        "summary": "너는 기뻤고, 밝았어."
    }
