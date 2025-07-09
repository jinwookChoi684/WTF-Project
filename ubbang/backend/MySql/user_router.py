# MySql/user_router.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .database import get_db
from .models import User

router = APIRouter()

class UserUpdateRequest(BaseModel):
    pk: int
    name: str
    gender: str
    mode: str
    worry: str
    tf:str

@router.patch("/update-user")
def update_user(data: UserUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.pk == data.pk).first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    user.name = data.name
    user.gender = data.gender
    user.mode = data.mode
    user.tf=data.tf
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
        "age": user.age,
        "tf":user.tf
    }
