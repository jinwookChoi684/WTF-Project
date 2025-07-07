from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from app import chat, diary
from MySql.database import SessionLocal, engine, Base
from MySql.models import User
from MySql.schemas import UserCreate, UserLogin, UserLoginResponse
from MySql.user_router import router as user_router
import httpx, logging, os

load_dotenv()

# 환경변수 로드
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("REDIRECT_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI()
app.include_router(chat.router)
app.include_router(diary.router)
# app.include_router(user_router)
app.include_router(user_router, prefix="/users", tags=["users"])  # ✅ 등록

# 미들웨어 추가 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 초기화
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ DB 연결 및 테이블 생성 완료")
except SQLAlchemyError as e:
    logger.error(f"❌ DB 연결 실패: {e}")

# DB 세션 생성 함수
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 비밀번호 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

@app.get("/")
async def root():
    return {"message": "서버 켜짐"}

# ✅ 기존 로그인 API 복구
@app.post("/login", response_model=UserLoginResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.userId == user.userId).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

    return {
        "pk": db_user.pk,
        "userId": db_user.userId,
        "name": db_user.name,
        "gender": db_user.gender,
        "mode": db_user.mode,
        "worry": db_user.worry,
        "birthDate": str(db_user.birthDate),
        "loginMethod": "이메일 계정",
        "isAnonymous": False
    }

# ✅ 구글 로그인 진입점
@app.get("/auth/google/login")
def google_login():
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(url)

# ✅ 구글 로그인 콜백
@app.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="코드 없음")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="토큰 획득 실패")

    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    user_info = user_resp.json()

    email = user_info.get("email")
    name = user_info.get("name")
    social_id = user_info.get("id")

    user = db.query(User).filter(User.userId == email).first()
    if not user:
        user = User(
            userId=email,
            name=name,
            email=email,
            password="",
            socialId=social_id,
            gender="",
            birthDate=None,
            worry="",
            mode="",
            age=0,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return RedirectResponse(f"http://localhost:3000/extra-info?pk={user.pk}")

# ✅ 추가 정보 업데이트 API
class ExtraInfoUpdate(BaseModel):
    pk: int
    gender: str
    birthDate: str
    worry: str
    mode: str
    age: int

@app.patch("/users/update-info")
async def update_extra_info(info: ExtraInfoUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.pk == info.pk).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자 없음")

    user.gender = info.gender
    user.birthDate = info.birthDate
    user.worry = info.worry
    user.mode = info.mode
    user.age = info.age

    db.commit()
    db.refresh(user)

    return {
        "pk": user.pk,
        "userId": user.userId,
        "name": user.name,
        "gender": user.gender,
        "mode": user.mode,
        "worry": user.worry,
        "birthDate": str(user.birthDate),
        "loginMethod": "Google OAuth",
        "isAnonymous": False
    }

# 회원가입
@app.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.userId == user.userId).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        userId=user.userId,
        name=user.name,
        password=hashed_password,
        email=user.email,
        gender=user.gender,
        birthDate=user.birthDate,
        worry=user.worry,
        mode=user.mode,
        age=user.age,
        socialId=user.socialId,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "pk": new_user.pk,
        "userId": new_user.userId,
        "name": new_user.name,
        "gender": new_user.gender,
        "mode": new_user.mode,
        "worry": new_user.worry,
        "birthDate": str(new_user.birthDate),
        "loginMethod": "이메일 계정",
    }