from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import httpx, os, urllib.parse
from fastapi import Request, APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from datetime import datetime
import os, httpx
from MySql.database import get_db
from MySql.models import User
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/naver/login")
def naver_login():
    client_id = os.getenv("NAVER_CLIENT_ID")
    redirect_uri = os.getenv("NAVER_REDIRECT_URI")
    state = "RANDOM_STATE"

    login_url = (
        f"https://nid.naver.com/oauth2.0/authorize?"
        f"response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&state={state}"
    )

    return RedirectResponse(login_url)


@router.post("/naver/token")
async def naver_token(req: Request, db: Session = Depends(get_db)):
    data = await req.json()
    code = data.get("code")
    state = data.get("state")

    # 1. access token 요청
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://nid.naver.com/oauth2.0/token",
            params={
                "grant_type": "authorization_code",
                "client_id": os.getenv("NAVER_CLIENT_ID"),
                "client_secret": os.getenv("NAVER_CLIENT_SECRET"),
                "code": code,
                "state": state,
            },
        )
    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return JSONResponse(status_code=400, content={"success": False, "message": "access_token 없음"})

    # 2. 사용자 정보 요청
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        user_resp = await client.get("https://openapi.naver.com/v1/nid/me", headers=headers)

    user_info = user_resp.json().get("response", {})
    social_id = user_info.get("id")
    email = user_info.get("email")
    name = user_info.get("name", "네이버 사용자")
    birthyear = user_info.get("birthyear")
    birthday = user_info.get("birthday")
    gender_raw = user_info.get("gender")
    gender = {"M": "male", "F": "female"}.get(gender_raw.upper(), None) if gender_raw else None

    birth_date = None
    age = None
    if birthyear and birthday:
        try:
            birth_date = datetime.strptime(f"{birthyear}-{birthday}", "%Y-%m-%d").date()
            age = datetime.today().year - int(birthyear)
        except:
            pass

    # 3. 기존 회원 조회 or 생성
    user = db.query(User).filter(User.socialId == social_id).first()
    if not user:
        new_user = User(
            userId=email,
            name=name,
            password="",
            email=email,
            birthDate=birth_date,
            gender=gender,
            socialId=social_id,
            age=age,
            mode="반말",
            tf="T"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user

    # 4. JWT 생성 및 Redis 저장
    access_token = create_access_token(data={"sub": user.userId})
    refresh_token = create_refresh_token(data={"sub": user.userId})
    store_access_token(user.pk, access_token)
    store_refresh_token(user.pk, refresh_token)

    # 5. 최종 응답
    res = JSONResponse(content={
        "success": True,
        "access_token": access_token,
        "user": {
            "pk": user.pk,
            "name": user.name,
            "userId": user.userId,
            "gender": user.gender,
            "mode": user.mode,
            "worry": user.worry,
            "birthDate": user.birthDate.isoformat() if user.birthDate else None,
            "loginMethod": "naver",
            "age": user.age,
            "tf": user.tf
        }
    })
    res.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        secure=False,
        samesite="lax"
    )
    return res
