from locust import HttpUser, task, between
import random
import string

class URLShortenerUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Регистрация и логин при старте"""
        self.username = f"user_{random.randint(1, 10000)}"
        self.password = "password123"
        
        # Регистрация
        self.client.post("/api/v1/users/register", json={
            "email": f"{self.username}@example.com",
            "username": self.username,
            "password": self.password
        })
        
        # Логин
        response = self.client.post("/api/v1/users/login", json={
            "username": self.username,
            "password": self.password
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.created_links = []
    
    @task(3)
    def create_short_link(self):
        """Создание короткой ссылки"""
        url = f"https://example.com/page{random.randint(1, 1000)}"
        
        # Иногда с кастомным алиасом
        if random.random() < 0.3:
            alias = ''.join(random.choices(string.ascii_lowercase, k=8))
            response = self.client.post("/api/v1/links/shorten", json={
                "original_url": url,
                "custom_alias": alias
            }, headers=self.headers if random.random() < 0.5 else {})
        else:
            response = self.client.post("/api/v1/links/shorten", json={
                "original_url": url
            }, headers=self.headers if random.random() < 0.5 else {})
        
        if response.status_code == 201:
            data = response.json()
            self.created_links.append(data["short_code"])
    
    @task(2)
    def get_link_stats(self):
        """Получение статистики"""
        if self.created_links:
            short_code = random.choice(self.created_links)
            self.client.get(f"/api/v1/links/{short_code}/stats")
    
    @task(1)
    def redirect_to_link(self):
        """Переход по ссылке"""
        if self.created_links:
            short_code = random.choice(self.created_links)
            self.client.get(f"/{short_code}", allow_redirects=False)
    
    @task(1)
    def search_links(self):
        """Поиск ссылок"""
        self.client.get("/api/v1/links/search", params={
            "original_url": "example.com"
        })
    
    def on_stop(self):
        """Удаление созданных ссылок при завершении"""
        for short_code in self.created_links:
            self.client.delete(f"/api/v1/links/{short_code}", headers=self.headers)