from fastapi import APIRouter, HTTPException, Depends, Body, Request, Query ,Response,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional
import os
from dotenv import load_dotenv
import logging
from sqlalchemy.exc import SQLAlchemyError
# 경로 문제 해결
import sys

from sympy import false

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from MySql.database import get_db
from MySql.models import User
from MySql.schemas import UserCreate, UserLoginResponse
from utils.jwt_utils import create_access_token, create_refresh_token
from utils.token_storage import store_refresh_token_to_db
from utils.token_storage import get_refresh_token_from_db

# 환경변수 로드
load_dotenv()
JWT_SECRET = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/users")



# ✅ 모델 정의
class UserUpdateRequest(BaseModel):
    pk: int
    name: Optional[str] = None
    gender: Optional[str] = None
    mode: Optional[str] = None
    worry: Optional[str] = None
    tf: Optional[str] = None
    pushEnabled: Optional[bool] = None
    pushTime: Optional[str] = None

class LoginRequest(BaseModel):
    userId: str
    password: str


# ✅ GET /users/{pk}
@router.get("/{pk}")
def get_user(pk: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.pk == pk).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ✅ PATCH /users/update-user
@router.patch("/update-user")
def update_user(data: UserUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.pk == data.pk).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    if data.name is not None:
        user.name = data.name
    if data.gender is not None:
        user.gender = data.gender
    if data.mode is not None:
        user.mode = data.mode
    if data.worry is not None:
        user.worry = data.worry
    if data.tf is not None:
        user.tf = data.tf
    if data.pushEnabled is not None:
        user.push_enabled = data.pushEnabled
    if data.pushTime is not None:
        user.push_time = data.pushTime

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
        "loginMethod": "이메일 계정",
        "age": user.age,
        "tf": user.tf,
        "pushEnabled": user.push_enabled,
        "pushTime": user.push_time,
    }



@router.post("/signup")
def signup(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    logger.info(f"🚀 /signup 요청 도착! 사용자 ID: {user.userId}")

    try:
        # 아이디 중복 확인
        existing_user = db.query(User).filter(User.userId == user.userId).first()
        if existing_user:
            logger.warning(f"⚠️ 이미 존재하는 아이디: {user.userId}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 아이디입니다."
            )

        # 비밀번호 해시
        hashed_password = pwd_context.hash(user.password)

        # 유저 생성
        new_user = User(
            userId=user.userId,
            name=user.name,
            password=hashed_password,
            email=user.email,
            gender=user.gender,
            birthDate=user.birthDate,
            socialId=user.socialId,
            worry=user.worry,
            mode=user.mode,
            age=user.age,
            tf=user.tf
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"✅ 회원가입 성공: {new_user.userId}")

        # ✅ JWT 토큰 생성
        access_token = create_access_token(data={"sub": str(new_user.pk)})
        refresh_token = create_refresh_token(data={"sub": str(new_user.pk)})

        # ✅ Refresh 토큰 DB에 저장
        store_refresh_token_to_db(new_user, refresh_token, db)

        # ✅ 쿠키에 refresh_token 저장

        # FastAPI 배포 환경
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,  # ✅ HTTPS만 허용
            samesite="none",  # ✅ cross-origin 허용
            domain=".ubbangfeeling.com",  # ✅ 선택: 전체 도메인 공유할 때
            path="/",
            max_age=60 * 60 * 24 * 7,
        )

        # ✅ 프론트로 access_token 전달
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "pk": new_user.pk,
            "userId": new_user.userId,
            "name": new_user.name,
            "gender": new_user.gender,
            "mode": new_user.mode,
            "worry": new_user.worry,
            "birthDate": str(new_user.birthDate),
            "age": new_user.age,
            "tf": new_user.tf
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ 회원가입 중 DB 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원가입 중 데이터베이스 오류가 발생했습니다."
        )


# ✅ POST /users/login
@router.post("/login")
def login(data: LoginRequest = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userId == data.userId).first()

    if not user or not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다.")

    access_token = create_access_token({"sub": str(user.pk)})
    refresh_token = create_refresh_token({"sub": str(user.pk)})

    store_refresh_token_to_db(user, refresh_token, db)  # ✅ DB 저장만

    response = JSONResponse(content={
        "access_token": access_token,
        "pk": user.pk,
        "userId": user.userId,
        "name": user.name,
        "gender": user.gender,
        "mode": user.mode,
        "worry": user.worry,
        "birthDate": str(user.birthDate),
        "loginMethod": "이메일 계정",
        "age": user.age,
        "tf": user.tf
    })


    # FastAPI 배포 환경
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # ✅ HTTPS만 허용
        samesite="none",  # ✅ cross-origin 허용
        domain=".ubbangfeeling.com",  # ✅ 선택: 전체 도메인 공유할 때
        path="/",
        max_age=60 * 60 * 24 * 7,
    )

    return response


# ✅ POST /users/refresh
@router.post("/refresh")
def refresh_access_token(request: Request, db: Session = Depends(get_db)):
    try:
        print("🍪 모든 쿠키:", request.cookies)
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="리프레시 토큰이 없습니다.")

        try:
            payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="리프레시 토큰 디코딩 실패")

        user_pk = int(payload.get("sub"))
        saved_token = get_refresh_token_from_db(user_pk, db)  # ✅ DB에서 조회

        if saved_token != refresh_token:
            raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")

        new_access_token = create_access_token({"sub": str(user_pk)})
        return JSONResponse(content={"access_token": new_access_token})

    except Exception as e:
        logger.exception("❌ 서버 오류:")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")


# ✅ GET /users/diary
@router.get("/diary")
def get_diary(pk: int = Query(...), db: Session = Depends(get_db)):
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


# 알람 푸쉬
import json
class PushSubscription(BaseModel):
    endpoint: str
    keys: dict

class SubscriptionRequest(BaseModel):
    subscription: PushSubscription
    notify_time: str

@router.post("/save-subscription")
async def save_subscription(data: SubscriptionRequest):
    try:
        # 구독 정보 저장 (간단히 JSON 파일로 저장)
        os.makedirs("subscriptions", exist_ok=True)

        with open("subscriptions/latest.json", "w") as f:
            json.dump({
                "endpoint": data.subscription.endpoint,
                "keys": data.subscription.keys,
                "notify_time": data.notify_time,
            }, f, indent=2)

        return {"message": "구독 정보 저장 완료 ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))