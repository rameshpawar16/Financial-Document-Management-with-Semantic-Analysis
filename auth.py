from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException

SECRET_KEY = "nimap-secret"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["argon2"],deprecated="auto")


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)


def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)