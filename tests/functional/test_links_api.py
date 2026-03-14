def test_create_short_link_anonymous(client):
    """Тест создания ссылки анонимным пользователем"""
    response = client.post("/api/v1/links/shorten", json={
        "original_url": "https://example.com"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert data["original_url"] == "https://example.com/"
    assert data["clicks"] == 0
    assert data["is_active"] is True

def test_create_short_link_with_custom_alias(client):
    """Тест создания ссылки с кастомным алиасом"""
    response = client.post("/api/v1/links/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": "myapi"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == "myapi"
    assert data["custom_alias"] == "myapi"

def test_create_short_link_duplicate_alias(client):
    """Тест на дублирование алиаса"""
    client.post("/api/v1/links/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": "duplicate"
    })
    
    response = client.post("/api/v1/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "duplicate"
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Custom alias already exists"

def test_create_short_link_with_expiry(client):
    """Тест создания ссылки с временем жизни"""
    response = client.post("/api/v1/links/shorten", json={
        "original_url": "https://example.com",
        "expires_at": "2025-12-31T23:59:59"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["expires_at"] == "2025-12-31T23:59:59"

def test_create_short_link_invalid_url(client):
    """Тест на невалидный URL"""
    response = client.post("/api/v1/links/shorten", json={
        "original_url": "not-a-url"
    })
    
    assert response.status_code == 422

def test_get_link_stats(client, test_link):
    """Тест получения статистики"""
    response = client.get(f"/api/v1/links/{test_link.short_code}/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == test_link.short_code
    assert data["original_url"] == test_link.original_url
    assert data["clicks"] == 0
    assert "short_url" in data

def test_get_nonexistent_link_stats(client):
    """Тест статистики для несуществующей ссылки"""
    response = client.get("/api/v1/links/nonexistent/stats")
    
    assert response.status_code == 404

def test_update_link_authorized(client, test_link, user_token):
    """Тест обновления ссылки с авторизацией"""
    response = client.put(
        f"/api/v1/links/{test_link.short_code}",
        json={"original_url": "https://updated.com"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == "https://updated.com/"

def test_update_link_unauthorized(client, test_link):
    """Тест обновления ссылки без авторизации"""
    response = client.put(
        f"/api/v1/links/{test_link.short_code}",
        json={"original_url": "https://updated.com"}
    )
    
    assert response.status_code == 401

def test_delete_link_authorized(client, test_link, user_token):
    """Тест удаления ссылки с авторизацией"""
    response = client.delete(
        f"/api/v1/links/{test_link.short_code}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 204

def test_delete_link_unauthorized(client, test_link):
    """Тест удаления ссылки без авторизации"""
    response = client.delete(f"/api/v1/links/{test_link.short_code}")
    
    assert response.status_code == 401

def test_search_links(client, test_user, db_session):
    """Тест поиска по оригинальному URL"""
    from app.models.link import Link
    links = [
        Link(short_code="search1", original_url="https://google.com/search", user_id=test_user.id),
        Link(short_code="search2", original_url="https://google.com/maps", user_id=test_user.id),
        Link(short_code="other", original_url="https://github.com", user_id=test_user.id)
        ]
    for link in links:
        db_session.add(link)
        db_session.commit()
    response = client.get("/api/v1/links/search", params={"original_url": "google"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("google" in item["original_url"] for item in data)