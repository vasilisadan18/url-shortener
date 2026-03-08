from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from core.database import get_db
from core.security import decode_token
from models.user import User
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login", auto_error=False)

def get_current_user(
    token: str= Depends(oauth2_scheme),
    db: Session= Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    payload = decode_token(token)
    if not payload:
        raise credentials_exception
    
    user_id = payload.get("user_id")
    if not user_id:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
    
    return user

def get_optional_user(
    token: str= Depends(oauth2_scheme),
    db: Session= Depends(get_db)
) -> Optional[User]:
    if not token:
        return None
    
    payload= decode_token(token)
    if not payload:
        return None
    
    user_id =payload.get("user_id")
    if not user_id:
        return None
    
    return db.query(User).filter(User.id == user_id).first()