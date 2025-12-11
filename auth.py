import streamlit as st
import hashlib
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

@dataclass
class User:
    """Класс пользователя"""
    username: str
    email: str
    password_hash: str
    created_at: str
    preferences: Dict = None
    reading_stats: Dict = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {
                "favorite_genres": [],
                "favorite_authors": [],
                "reading_goals": {}
            }
        if self.reading_stats is None:
            self.reading_stats = {
                "books_read": 0,
                "pages_read": 0,
                "reading_days": 0,
                "avg_rating": 0
            }

class UserManager:
    """Менеджер пользователей"""
    
    def __init__(self, users_file="users.json"):
        self.users_file = users_file
        self.users = self._load_users()
        self.current_user = None
    
    def _load_users(self) -> Dict[str, User]:
        """Загрузка пользователей из файла"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                    return {username: User(**data) for username, data in users_data.items()}
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Сохранение пользователей в файл"""
        users_data = {username: asdict(user) for username, user in self.users.items()}
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    
    def hash_password(self, password: str) -> str:
        """Хэширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username: str, email: str, password: str) -> bool:
        """Регистрация нового пользователя"""
        if username in self.users:
            return False, "Пользователь с таким именем уже существует"
        
        if any(user.email == email for user in self.users.values()):
            return False, "Пользователь с таким email уже существует"
        
        password_hash = self.hash_password(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.users[username] = new_user
        self._save_users()
        return True, "Регистрация успешна!"
    
    def login(self, username: str, password: str) -> bool:
        """Вход пользователя"""
        if username not in self.users:
            return False, "Пользователь не найден"
        
        user = self.users[username]
        if user.password_hash == self.hash_password(password):
            self.current_user = user
            return True, "Вход выполнен успешно!"
        else:
            return False, "Неверный пароль"
    
    def logout(self):
        """Выход пользователя"""
        self.current_user = None
    
    def get_current_user(self) -> Optional[User]:
        """Получение текущего пользователя"""
        return self.current_user
    
    def update_user_preferences(self, username: str, preferences: Dict):
        """Обновление предпочтений пользователя"""
        if username in self.users:
            self.users[username].preferences.update(preferences)
            self._save_users()