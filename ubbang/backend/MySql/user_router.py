# MySql/user_router.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from MySql.database import get_db
from MySql.models import User
from passlib.context import CryptContext
from MySql.schemas import UserCreate

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserUpdateRequest(BaseModel):
    pk: int
    name: str
    gender: str
    mode: str
    worry: str

# ✅ GET /users/{pk}
@router.get("/{pk}")
def get_user(pk: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.pk == pk).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/update-user")
def update_user(data: UserUpdateRequest, db: Session = Depends(get_db)):
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
    }