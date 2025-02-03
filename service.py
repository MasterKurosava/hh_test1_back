from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from repository import get_user_by_email, create_user
from sqlalchemy.orm import Session

# Хеширование пароля через bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)  # Генерирую хеш пароля

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)  # Проверяю пароль

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Создаю JWT-токен с временем жизни"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def register_user_service(db: Session, first_name: str, last_name: str, email: str, password: str):
    """Проверяю, есть ли пользователь, если нет — создаю нового"""
    if get_user_by_email(db, email):
        return None  # Email уже занят
    return create_user(db, first_name, last_name, email, get_password_hash(password))

def authenticate_user(db: Session, email: str, password: str):
    """Проверяю email и пароль, если всё ок — возвращаю пользователя"""
    user = get_user_by_email(db, email)
    return user if user and verify_password(password, user.password) else None
