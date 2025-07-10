from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from MySql.database import SessionLocal, engine, Base
from MySql.models import User
from MySql.schemas import UserCreate, UserLogin, UserLoginResponse
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel
from MySql import models
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import os
import logging  # 로깅 모듈 임포트
from app import chat
from app import diary
from MySql.user_router import router as user_router
from naver_oauth import router as naver_router
import asyncio
# from app.idle_checker import start_idle_checker
# from redis_utiles.redis_client import save_chat_message, get_recent_messages, cache_user_info

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()
app.include_router(chat.router)
app.include_router(diary.router)
app.include_router(user_router)
app.include_router(naver_router)



origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 데이터베이스 연결 성공 및 테이블 생성 완료")
except SQLAlchemyError as e:
    logger.critical(f"❌ 데이터베이스 연결 또는 테이블 생성 실패: {e}")

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/")
async def root():  # 비동기 함수로 변경
    return {"message": "서버 잘 켜졌어! 🎉"}

@app.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"🚀 /signup 요청 도착! 사용자 ID: {user.userId}")

    db_user = db.query(User).filter(User.userId == user.userId).first()
    if db_user:
        logger.warning(f"⚠️ 이미 존재하는 아이디: {user.userId}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 아이디입니다."
        )

    hashed_password = pwd_context.hash(user.password)

    new_user = User(
        userId=user.userId,
        name=user.name,
        password=hashed_password,
        email=user.email,
        birthDate=user.birthDate,
        gender=user.gender,
        mode=user.mode,
        worry=user.worry,
        socialId=user.socialId,
        age=user.age,
        tf=user.tf
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"✅ 회원가입 성공: {new_user.userId}")

        # Redis 캐싱
        # cache_user_info(
        #     new_user.userId,
        #     {
        #         "name": new_user.name,
        #         "email": new_user.email,
        #         "gender": new_user.gender,
        #         "birthDate": str(new_user.birthDate),
        #     }
        # )
        return {"message": "회원가입 성공",
                "pk": new_user.pk,
                "userId": new_user.userId,
                "name": new_user.name,
                "gender": new_user.gender,
                "mode": new_user.mode,
                "worry": new_user.worry,
                "birthDate": new_user.birthDate.strftime("%Y-%m-%d") if new_user.birthDate else None,  # ✅ 고침
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

# 비회원 가입시 로그인 강제 처리
@app.post("/users")
async def create_user_alias(user: UserCreate, db: Session = Depends(get_db)):
    return await signup(user, db)


@app.post("/login", response_model=UserLoginResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"🚪 로그인 시도: {user.userId}")
    db_user = db.query(User).filter(User.userId == user.userId).first()

    if not db_user:
        logger.warning(f"❌ 사용자 없음: {user.userId}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 사용자입니다."
        )

    if not pwd_context.verify(user.password, db_user.password):
        logger.warning(f"❌ 비밀번호 불일치: {user.userId}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 일치하지 않습니다."
        )

    logger.info(f"✅ 로그인 성공: {db_user.userId}")
    return {
        "pk": db_user.pk,
        "userId": db_user.userId,
        "name": db_user.name,
        "gender": db_user.gender,
        "mode": db_user.mode,
        "worry": db_user.worry,
        "birthDate": str(db_user.birthDate),
        "loginMethod": "이메일 계정",
        "isAnonymous": False,
        "age": db_user.age,
        "tf": db_user.tf

    }

class DeleteRequest(BaseModel):
    userId: str

@app.post("/delete-user")
async def delete_user(request: DeleteRequest, db: Session = Depends(get_db)):
    logger.info(f"🗑️ 사용자 삭제 요청: {request.userId}")
    user_to_delete = db.query(models.User).filter(models.User.userId == request.userId).first()
    if not user_to_delete:
        logger.warning(f"❌ 삭제할 사용자 없음: {request.userId}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    try:
        db.delete(user_to_delete)
        db.commit()
        logger.info(f"✅ 사용자 삭제 성공: {request.userId}")
        return {"message": "User deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ 사용자 삭제 중 DB 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 삭제 중 데이터베이스 오류가 발생했습니다."
        )

class ChatInput(BaseModel):
    userId: str
    message: str

@app.post("/chat")
async def chat_with_ai(chat: ChatInput):
    logger.info(f"💬 챗 요청 수신 - userId: {chat.userId}, message: {chat.message[:50]}...")

    if not OPENAI_API_KEY:
        logger.error("OpenAI API 키가 없어 AI 응답을 생성할 수 없습니다.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 서비스 준비 중입니다. 잠시 후 다시 시도해주세요."
        )

    try:
        context = []  # 임시로 빈 리스트, 실제 Redis 연동 시 수정
        prompt_messages = [
            {"role": "system", "content": "You are a warm, empathetic assistant replying in Korean."},
            {"role": "user", "content": chat.message},
        ]
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=prompt_messages
            )
            reply_text = response.choices[0].message.content.strip()
            logger.info(f"✅ GPT 응답 성공 (userId: {chat.userId})")
        except Exception as gpt_error:
            logger.error(f"⚠️ GPT 호출 실패 (userId: {chat.userId}): {gpt_error}")
            reply_text = "죄송합니다. 현재 답변을 생성할 수 없습니다. 잠시 후 다시 시도해주세요."

        # Redis 저장
        # timestamp = datetime.now().isoformat()
        # await save_chat_message(
        #     pk=chat.userId,
        #     timestamp=timestamp,
        #     message=chat.message
        # )

        return {
            "context": context,
            "reply": reply_text,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"🔥 예기치 않은 서버 오류 발생 (userId: {chat.userId}): {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI 응답 생성 중 예기치 않은 서버 오류가 발생했습니다."
        )


# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(start_idle_checker())


# ✅ 감정 히스토리 및 컨텍스트 조회용 API
# @app.get("/chat/context/{pk}")
# def get_chat_context(pk: str):
#     messages = get_recent_messages(pk)
#     return {"recent_messages": messages}
#
# @app.get("/chat/emotions/{pk}")
# def get_emotions(pk: str, limit: int = 10):
#     records = get_emotion_history(pk, limit)
#     return {"emotion_history": records}
