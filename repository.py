from sqlalchemy.orm import Session
from models import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, first_name: str, last_name: str, email: str, password: str):
    user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
