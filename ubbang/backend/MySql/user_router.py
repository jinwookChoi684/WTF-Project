from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from MySql.database import get_db
from MySql.models import User
from passlib.context import CryptContext
from MySql.schemas import UserCreate
from MySql.models import User as UserModel

router = APIRouter(prefix="/users")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ✅ 유저 정보 수정용
class UserUpdateRequest(BaseModel):
    pk: int
    name: str
    gender: str
    mode: str
    worry: str
    tf: str

# ✅ 로그인 요청용
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

    user.name = data.name
    user.gender = data.gender
    user.mode = data.mode
    user.worry = data.worry
    user.tf = data.tf

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
        "age": user.age,
        "tf": user.tf
    }


# ✅ POST /users/signup
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
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
        socialId=user.socialId,
        worry=user.worry,
        mode=user.mode,
        age=user.age
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
        "age": new_user.age
    }


# ✅ POST /users/login
@router.post("/login")
def login(data: LoginRequest = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userId == data.userId).first()

    if not user or not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다.")

    return {
        "pk": user.pk,
        "userId": user.userId,
        "name": user.name,
        "gender": user.gender,
        "mode": user.mode,
        "worry": user.worry,
        "birthDate": str(user.birthDate),
        "age": user.age,
        "loginMethod": "이메일 계정",
        "tf": user.tf # 확인해보기


    }


from fastapi import Query
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
