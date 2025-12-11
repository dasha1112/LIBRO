import json
import os
from typing import Dict, List
from dataclasses import dataclass, field

@dataclass
class UserBookList:
    """Список книг пользователя"""
    name: str
    book_ids: List[int] = field(default_factory=list)
    description: str = ""

class UserListsManager:
    """Менеджер списков пользователей"""
    
    def __init__(self, data_file="user_lists.json"):
        self.data_file = data_file
        self.user_lists = self._load_data()
    
    def _load_data(self) -> Dict[str, Dict[str, UserBookList]]:
        """Загрузка данных из файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Преобразуем JSON в объекты
                    result = {}
                    for username, lists_dict in data.items():
                        result[username] = {}
                        for list_name, list_data in lists_dict.items():
                            result[username][list_name] = UserBookList(**list_data)
                    return result
            except:
                return {}
        return {}
    
    def _save_data(self):
        """Сохранение данных в файл"""
        # Преобразуем объекты в словари
        save_data = {}
        for username, lists_dict in self.user_lists.items():
            save_data[username] = {}
            for list_name, book_list in lists_dict.items():
                save_data[username][list_name] = {
                    "name": book_list.name,
                    "book_ids": book_list.book_ids,
                    "description": book_list.description
                }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    def get_user_lists(self, username: str) -> Dict[str, UserBookList]:
        """Получение списков пользователя"""
        return self.user_lists.get(username, {
            "reading": UserBookList("Читаю", [], "Книги, которые читаю сейчас"),
            "read": UserBookList("Прочитано", [], "Прочитанные книги"),
            "planned": UserBookList("Планирую", [], "Книги, которые планирую прочитать"),
            "dropped": UserBookList("Брошено", [], "Книги, которые бросил читать"),
            "favorites": UserBookList("Любимые", [], "Мои любимые книги")
        })
    
    def add_book_to_list(self, username: str, list_name: str, book_id: int):
        """Добавление книги в список"""
        if username not in self.user_lists:
            self.user_lists[username] = self.get_user_lists(username)
        
        if list_name not in self.user_lists[username]:
            self.user_lists[username][list_name] = UserBookList(list_name)
        
        if book_id not in self.user_lists[username][list_name].book_ids:
            self.user_lists[username][list_name].book_ids.append(book_id)
            self._save_data()
    
    def remove_book_from_list(self, username: str, list_name: str, book_id: int):
        """Удаление книги из списка"""
        if (username in self.user_lists and 
            list_name in self.user_lists[username] and
            book_id in self.user_lists[username][list_name].book_ids):
            
            self.user_lists[username][list_name].book_ids.remove(book_id)
            self._save_data()
    
    def move_book_between_lists(self, username: str, book_id: int, 
                                from_list: str, to_list: str):
        """Перемещение книги между списками"""
        self.remove_book_from_list(username, from_list, book_id)
        self.add_book_to_list(username, to_list, book_id)
    
    def get_books_in_list(self, username: str, list_name: str, 
                          book_db) -> List[Dict]:
        """Получение информации о книгах в списке"""
        if username not in self.user_lists or list_name not in self.user_lists[username]:
            return []
        
        book_ids = self.user_lists[username][list_name].book_ids
        books = book_db.books[book_db.books["id"].isin(book_ids)]
        
        # Сохраняем порядок как в списке
        ordered_books = []
        for book_id in book_ids:
            book_data = books[books["id"] == book_id]
            if not book_data.empty:
                ordered_books.append(book_data.iloc[0].to_dict())
        
        return ordered_books