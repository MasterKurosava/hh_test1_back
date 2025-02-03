from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserRegister, UserLogin
from service import register_user_service, authenticate_user, create_access_token

router = APIRouter()

@router.post("/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрирую пользователя, если email не занят"""
    user = register_user_service(db, user_data.first_name, user_data.last_name, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    return {"message": "Пользователь зарегистрирован"}

@router.post("/login")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Авторизую пользователя, если данные верные"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Неверные учетные данные")
    return {"access_token": create_access_token({"sub": user.email}), "token_type": "bearer"}

@router.get("/me")
def get_user_info(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Получаю информацию о пользователе из токена"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Токен отсутствует или некорректен")

    token = authorization.split("Bearer ")[1]
    
    from jose import jwt, JWTError
    from config import SECRET_KEY, ALGORITHM
    from repository import get_user_by_email

    try:
        email = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return {"first_name": user.first_name, "last_name": user.last_name, "email": user.email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Неверный или просроченный токен")
