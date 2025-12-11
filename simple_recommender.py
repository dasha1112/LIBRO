import pandas as pd
import streamlit as st
from typing import List, Dict

class SimpleRecommender:
    """Простая система рекомендаций на основе отзывов пользователя"""
    
    def __init__(self, book_db, book_page_manager):
        self.book_db = book_db
        self.book_page_manager = book_page_manager
    
    def get_recommendations(self, username: str, limit: int = 15) -> List[Dict]:
        """Получение рекомендаций на основе хороших отзывов пользователя"""
        # 1. Находим книги с хорошими отзывами (оценка 4-5)
        good_reviews_books = self._get_books_with_good_reviews(username)
        
        if not good_reviews_books:
            return self._get_popular_books(limit)
        
        # 2. Находим похожие книги
        recommendations = []
        seen_ids = set(good_reviews_books)  # Исключаем уже оцененные книги
        
        for book_id in good_reviews_books:
            similar_books = self._find_similar_books(book_id, seen_ids, limit=5)
            recommendations.extend(similar_books)
            seen_ids.update([b["id"] for b in similar_books])
        
        # 3. Убираем дубликаты и сортируем
        unique_recs = {}
        for rec in recommendations:
            if rec["id"] not in unique_recs:
                unique_recs[rec["id"]] = rec
        
        return list(unique_recs.values())[:limit]
    
    def _get_books_with_good_reviews(self, username: str) -> List[int]:
        """Получение ID книг с хорошими отзывами от пользователя"""
        good_books = []
        
        # Проверяем отзывы в book_page_manager
        for book_id_str, reviews in self.book_page_manager.reviews.items():
            for review in reviews:
                if review["username"] == username and review["rating"] >= 4:
                    good_books.append(int(book_id_str))
        
        return list(set(good_books))  # Убираем дубликаты
    
    def _find_similar_books(self, book_id: int, exclude_ids: set, limit: int = 5) -> List[Dict]:
        """Поиск похожих книг"""
        # Находим целевую книгу
        target_book = self.book_db.books[self.book_db.books["id"] == book_id]
        if target_book.empty:
            return []
        
        target = target_book.iloc[0]
        all_books = self.book_db.books
        
        similar_books = []
        
        for _, book in all_books.iterrows():
            # Пропускаем если книга уже в исключениях
            if book["id"] in exclude_ids:
                continue
            
            similarity_score = 0
            
            # По жанру
            if book["main_genre"] == target["main_genre"]:
                similarity_score += 3
            
            # По поджанру
            if book["sub_genre"] == target["sub_genre"]:
                similarity_score += 2
            
            # По автору (но не слишком много от одного автора)
            if book["author"] == target["author"]:
                similarity_score += 1
            
            # По настроению
            if (isinstance(book.get("mood"), list) and 
                isinstance(target.get("mood"), list)):
                common_moods = set(book["mood"]).intersection(set(target["mood"]))
                similarity_score += len(common_moods) * 0.5
            
            # По тропам
            if (isinstance(book.get("plot_tropes"), list) and 
                isinstance(target.get("plot_tropes"), list)):
                common_tropes = set(book["plot_tropes"]).intersection(set(target["plot_tropes"]))
                similarity_score += len(common_tropes) * 0.3
            
            if similarity_score > 0:
                book_dict = book.to_dict()
                book_dict["similarity_score"] = similarity_score
                similar_books.append(book_dict)
        
        # Сортируем по схожести и рейтингу
        similar_books.sort(key=lambda x: (x["similarity_score"], x["rating"]), reverse=True)
        
        return similar_books[:limit]
    
    def _get_popular_books(self, limit: int = 15) -> List[Dict]:
        """Получение популярных книг (если нет отзывов)"""
        all_books = self.book_db.books
        
        # Сортируем по рейтингу и году
        popular = all_books.sort_values(
            by=["rating", "year"], 
            ascending=[False, False]
        )
        
        return popular.head(limit).to_dict('records')