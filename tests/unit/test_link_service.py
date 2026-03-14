import pytest
from unittest.mock import Mock, patch
from app.services.link_service import LinkService
from app.schemas.link import LinkCreate
from app.models.link import Link

def test_generate_short_code_length():
    """Тест генерации короткого кода с правильной длиной"""
    code = LinkService.generate_short_code(6)
    assert len(code) == 6
    
    code = LinkService.generate_short_code(8)
    assert len(code) == 8

def test_generate_short_code_unique_chars():
    """Тест, что код состоит из допустимых символов"""
    code = LinkService.generate_short_code(10)
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    assert all(c in allowed_chars for c in code)

@patch('app.services.link_service.RedisCache')
def test_create_link_with_custom_alias(mock_redis, db_session, test_user):
    """Тест создания ссылки с кастомным алиасом"""
    link_data = LinkCreate(
        original_url="https://example.com",
        custom_alias="myalias"
    )
    
    link = LinkService.create_link(db_session, link_data, test_user.id)
    
    assert link.short_code == "myalias"
    assert link.custom_alias == "myalias"
    assert link.original_url == "https://example.com/"
    assert link.user_id == test_user.id
    mock_redis.set.assert_called_once()

@patch('app.services.link_service.RedisCache')
def test_create_link_without_alias(mock_redis, db_session, test_user):
    """Тест создания ссылки без кастомного алиаса"""
    link_data = LinkCreate(original_url="https://example.com")
    
    link = LinkService.create_link(db_session, link_data, test_user.id)
    
    assert link.short_code is not None
    assert len(link.short_code) == 6
    assert link.custom_alias is None
    mock_redis.set.assert_called_once()

def test_create_link_duplicate_alias(db_session, test_user):
    """Тест на ошибку при дублировании алиаса"""
    link_data = LinkCreate(
        original_url="https://example.com",
        custom_alias="duplicate"
    )
    
    # Создаем первую ссылку
    LinkService.create_link(db_session, link_data, test_user.id)
    
    # Пытаемся создать вторую с тем же алиасом
    with pytest.raises(ValueError, match="Custom alias already exists"):
        LinkService.create_link(db_session, link_data, test_user.id)

def test_get_link_by_short_code(db_session, test_link):
    """Тест получения ссылки по короткому коду"""
    link = LinkService.get_link(db_session, test_link.short_code)
    
    assert link is not None
    assert link.id == test_link.id
    assert link.original_url == test_link.original_url

@patch('app.services.link_service.RedisCache')
def test_record_click(mock_redis, db_session, test_link):
    """Тест увеличения счетчика кликов"""
    initial_clicks = test_link.clicks
    
    LinkService.record_click(db_session, test_link)
    
    assert test_link.clicks == initial_clicks + 1
    assert test_link.last_accessed_at is not None
    mock_redis.set.assert_called_once()

def test_update_link(db_session, test_link, test_user):
    """Тест обновления ссылки"""
    from app.schemas.link import LinkUpdate
    
    update_data = LinkUpdate(original_url="https://updated.com")
    
    updated_link = LinkService.update_link(db_session, test_link, update_data, test_user.id)
    
    assert updated_link.original_url == "https://updated.com/"
    assert updated_link.id == test_link.id

def test_update_link_permission_denied(db_session, test_link):
    """Тест на ошибку при обновлении чужой ссылки"""
    from app.schemas.link import LinkUpdate
    
    update_data = LinkUpdate(original_url="https://updated.com")
    wrong_user_id = "wrong-user-id"
    
    with pytest.raises(PermissionError, match="You don't have permission"):
        LinkService.update_link(db_session, test_link, update_data, wrong_user_id)

def test_delete_link(db_session, test_link, test_user):
    """Тест удаления ссылки"""
    link_id = test_link.id
    
    result = LinkService.delete_link(db_session, test_link, test_user.id)
    
    assert result is True
    deleted_link = db_session.query(Link).filter(Link.id == link_id).first()
    assert deleted_link is None

def test_search_by_original_url(db_session, test_user):
    """Тест поиска по оригинальному URL"""
    # Создаем несколько ссылок
    links_data = [
        ("https://google.com/search", "google1"),
        ("https://google.com/maps", "google2"),
        ("https://github.com", "github")
    ]
    
    for url, code in links_data:
        link = Link(
            short_code=code,
            original_url=url,
            user_id=test_user.id
        )
        db_session.add(link)
    db_session.commit()
    
    # Поиск по "google"
    results = LinkService.search_by_original_url(db_session, "google")
    assert len(results) == 2
    assert all("google" in r.original_url for r in results)
    
    # Поиск по "github"
    results = LinkService.search_by_original_url(db_session, "github")
    assert len(results) == 1
    assert results[0].short_code == "github"

def test_cleanup_expired_links(db_session, test_user):
    """Тест очистки истекших ссылок"""
    from datetime import datetime, timedelta
    
    # Создаем просроченную ссылку
    expired_link = Link(
        short_code="expired",
        original_url="https://expired.com",
        user_id=test_user.id,
        expires_at=datetime.utcnow() - timedelta(days=1)
    )
    db_session.add(expired_link)
    
    # Создаем активную ссылку
    active_link = Link(
        short_code="active",
        original_url="https://active.com",
        user_id=test_user.id,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    db_session.add(active_link)
    db_session.commit()
    
    count = LinkService.cleanup_expired_links(db_session)
    
    assert count == 1
    assert db_session.query(Link).filter(Link.short_code == "expired").first() is None
    assert db_session.query(Link).filter(Link.short_code == "active").first() is not None
    
def test_get_link_from_cache(db_session, test_link):
    """Тест получения ссылки из кэша"""
    with patch('app.services.link_service.RedisCache.get') as mock_cache:
        mock_cache.return_value = {
            "original_url": test_link.original_url,
            "is_active": True
        }
        link = LinkService.get_link(db_session, test_link.short_code)
        assert link is not None

def test_get_link_expired(db_session, test_user):
    """Тест получения истекшей ссылки"""
    from datetime import datetime, timedelta
    
    expired_link = Link(
        short_code="expired",
        original_url="https://expired.com",
        user_id=test_user.id,
        expires_at=datetime.utcnow() - timedelta(days=1)
    )
    db_session.add(expired_link)
    db_session.commit()
    
    link = LinkService.get_link(db_session, "expired")
    assert link is None