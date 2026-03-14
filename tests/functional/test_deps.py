import pytest
from fastapi import HTTPException
from app.api.deps import get_current_user, get_optional_user

def test_get_current_user_no_token():
    """Тест получения пользователя без токена"""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=None, db=None)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"

def test_get_optional_user_no_token():
    """Тест опционального пользователя без токена"""
    result = get_optional_user(token=None, db=None)
    assert result is None