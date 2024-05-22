from datetime import datetime, timedelta

import jwt
from sqlalchemy import select

from db import new_session
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = 'n24iunfg234ugn934g'
ALGORITHM = 'HS256'

def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(email: str, password: str):
    async with new_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not (user and verify_password(password, user.password)):
            return None
        return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt
    