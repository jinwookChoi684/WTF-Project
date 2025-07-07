from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from MySql.database import get_db
from MySql.models import User

router = APIRouter()

# ✅ Pydantic 모델 (요청용)
class UserUpdateRequest(BaseModel):
    pk: int
    gender: Optional[str] = None
    birthDate: Optional[str] = None  # ISO 형식 문자열 (예: "2000-01-01")
    worry: Optional[str] = None
    mode: Optional[str] = None
    age: Optional[int] = None

# ✅ GET /users/{pk}
@router.get("/{pk}")
def get_user(pk: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.pk == pk).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ✅ PATCH /users/update-info
@router.patch("/users/update-info")
def update_user_info(request: UserUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.pk == request.pk).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 업데이트 가능한 필드만 체크해서 수정
    if request.gender is not None:
        user.gender = request.gender
    if request.birthDate is not None:
        user.birthDate = request.birthDate
    if request.worry is not None:
        user.worry = request.worry
    if request.mode is not None:
        user.mode = request.mode
    if request.age is not None:
        user.age = request.age

    db.commit()
    db.refresh(user)
    return user
