from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from auth import SECRET_KEY, ALGORITHM
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")

def check_permission(required_role: str):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403, detail="Not authorized")
        return user
    return role_checker

def role_required(allowed_roles: list):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403,detail="Access Denied")
        return user
    return role_checker

ROLE_PERMISSIONS = {

    "admin": ["upload", "edit", "delete", "view"],

    "financial analyst": ["upload", "edit"],

    "auditor": ["review"],

    "client": ["view"]

}

def permission_required(permission: str):
    def checker(user=Depends(get_current_user)):
        role = user["role"]
        if permission not in ROLE_PERMISSIONS.get(role, []):
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )
        return user
    return checker
