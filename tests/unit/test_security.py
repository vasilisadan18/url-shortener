import pytest
from jose import jwt
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token
)
from app.core.config import settings

def test_password_hashing():
    """Тест хеширования и проверки пароля"""
    password = "testpassword123"
    
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    """Тест создания JWT токена"""
    data = {"sub": "testuser", "user_id": "123"}
    
    token = create_access_token(data)
    assert token is not None
    
    # Проверяем, что токен можно декодировать
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "testuser"
    assert payload["user_id"] == "123"
    assert "exp" in payload

def test_decode_valid_token():
    """Тест декодирования валидного токена"""
    data = {"sub": "testuser", "user_id": "123"}
    token = create_access_token(data)
    
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert payload["user_id"] == "123"

def test_decode_invalid_token():
    """Тест декодирования невалидного токена"""
    invalid_token = "invalid.token.string"
    
    payload = decode_token(invalid_token)
    assert payload is None

def test_verify_password_error():
    """Тест ошибки верификации пароля"""
    result = verify_password("test", None)
    assert result is False