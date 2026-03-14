def test_register_user(client):
    """Тест регистрации пользователя с отладкой"""
    import json
    
    # Тестовые данные
    payload = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "testpass123"
    }
    
    print("\n" + "="*50)
    print("🔍 ТЕСТ РЕГИСТРАЦИИ")
    print("="*50)
    print(f"📦 Отправляемые данные: {json.dumps(payload, indent=2)}")
    print(f"📌 URL: /api/v1/users/register")
    
    # Отправляем запрос
    response = client.post("/api/v1/users/register", json=payload)
    
    print(f"\n📊 Статус ответа: {response.status_code}")
    print(f"📄 Тело ответа: {response.text}")
    print("="*50 + "\n")
    
    # Проверяем результат
    if response.status_code == 200:
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert "id" in data
    else:
        # Если ошибка, выводим детали
        print(f"❌ Ошибка! Код: {response.status_code}")
        if response.status_code == 422:
            print("⚠️  Проблема с валидацией данных")
        elif response.status_code == 400:
            print("⚠️  Пользователь уже существует")
        elif response.status_code == 500:
            print("⚠️  Ошибка сервера")
    
    assert response.status_code == 200

def test_login_user(client, test_user):
    """Тест входа пользователя"""
    response = client.post("/api/v1/users/login", json={
        "username": test_user.username,
        "password": "testpass123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Тест входа с неправильным паролем"""
    response = client.post("/api/v1/users/login", json={
        "username": test_user.username,
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_nonexistent_user(client):
    """Тест входа несуществующего пользователя"""
    response = client.post("/api/v1/users/login", json={
        "username": "nonexistent",
        "password": "testpass123" 
    })
    
    assert response.status_code == 401

def test_register_user_invalid_email(client):
    """Тест регистрации с невалидным email"""
    response = client.post("/api/v1/users/register", json={
        "email": "not-an-email",
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 422