def test_redirect_to_original(client, test_link):
    """Тест редиректа на оригинальный URL"""
    response = client.get(f"/api/v1/links/{test_link.short_code}", follow_redirects=False)
    
    assert response.status_code == 307
    assert response.headers["location"] == test_link.original_url

def test_root_redirect(client, test_link):
    """Тест редиректа через корневой путь"""
    response = client.get(f"/{test_link.short_code}", follow_redirects=False)
    
    assert response.status_code == 307
    assert response.headers["location"] == test_link.original_url

def test_redirect_nonexistent_link(client):
    """Тест редиректа для несуществующей ссылки"""
    response = client.get("/api/v1/links/nonexistent", follow_redirects=False)
    
    assert response.status_code == 404

def test_redirect_expired_link(client, db_session, test_user):
    """Тест редиректа для истекшей ссылки"""
    from datetime import datetime, timedelta
    from app.models.link import Link
    
    expired_link = Link(
        short_code="expired",
        original_url="https://expired.com",
        user_id=test_user.id,
        expires_at=datetime.utcnow() - timedelta(days=1),
        is_active=False
    )
    db_session.add(expired_link)
    db_session.commit()
    
    response = client.get("/api/v1/links/expired", follow_redirects=False)
    
    assert response.status_code == 404