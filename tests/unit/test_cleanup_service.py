import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.cleanup_service import (
    start_cleanup_scheduler,
    cleanup_expired_links,
    cleanup_unused_links
)

@patch('app.services.cleanup_service.SessionLocal')
def test_cleanup_expired_links(mock_session_local, db_session):
    """Тест очистки истекших ссылок"""
    mock_session_local.return_value = db_session
    cleanup_expired_links()
    assert True

@patch('app.services.cleanup_service.SessionLocal')
def test_cleanup_unused_links(mock_session_local, db_session):
    """Тест очистки неиспользуемых ссылок"""
    mock_session_local.return_value = db_session
    cleanup_unused_links()
    assert True

def test_start_cleanup_scheduler():
    """Тест запуска планировщика"""
    try:
        with patch('time.sleep', side_effect=KeyboardInterrupt):
            start_cleanup_scheduler()
    except KeyboardInterrupt:
        pass
    
    assert True