from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from MySql.database import get_db
from MySql.models import User
from redis_client import r
import jwt
from datetime import datetime, timedelta
import os

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "devsecret")
ALGORITHM = "HS256"

class UserUpdateRequest(BaseModel):
    pk: int
    name: str
    gender: str
    mode: str
    worry: str

# --------------------------
# 로그인/토큰/세션 관련 함수 추가
def verify_token(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="토큰 누락")
    access_token = token.split(" ")[1]
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰 만료")
    session_key = f"session:{user_id}"
    redis_token = r.get(session_key)
    if not redis_token or redis_token != access_token:
        raise HTTPException(status_code=401, detail="세션 만료/비정상")
    return user_id

# --------------------------
# 프로필 수정 API (로그인된 유저만)
@router.patch("/update-user")
def update_user(
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token)
):
    user = db.query(User).filter(User.pk == data.pk).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user.name = data.name
    user.gender = data.gender
    user.mode = data.mode
    user.worry = data.worry
    db.commit()
    db.refresh(user)
    return {
        "pk": user.pk,
        "userId": user.userId,
        "name": user.name,
        "gender": user.gender,
        "mode": user.mode,
        "worry": user.worry,
        "birthDate": user.birthDate.strftime("%Y-%m-%d") if user.birthDate else None,
        "loginMethod": user.loginMethod if hasattr(user, "loginMethod") else None,
        "age": user.age
    }

# --------------------------
# (로그인/회원가입/로그아웃 등도 같은 router에)
