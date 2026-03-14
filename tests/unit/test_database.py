import pytest
from app.core.database import get_db

def test_get_db():
    """Тест получения сессии БД"""
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    try:
        next(db_gen)
    except StopIteration:
        pass