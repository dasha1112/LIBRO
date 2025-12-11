import streamlit as st
import pandas as pd
from typing import Dict, List
import json
import os

class BookPageManager:
    """Менеджер для отображения детальных страниц книг"""
    
    def __init__(self, book_db, auth_manager, lists_manager):
        self.book_db = book_db
        self.auth_manager = auth_manager
        self.lists_manager = lists_manager
        self.reviews_file = "book_reviews.json"
        self.reviews = self._load_reviews()
    
    def _load_reviews(self) -> Dict:
        """Загрузка отзывов из файла"""
        if os.path.exists(self.reviews_file):
            try:
                with open(self.reviews_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_reviews(self):
        """Сохранение отзывов в файл"""
        with open(self.reviews_file, 'w', encoding='utf-8') as f:
            json.dump(self.reviews, f, ensure_ascii=False, indent=2)
    
    def get_book_details(self, book_id: int) -> Dict:
        """Получение детальной информации о книге"""
        book_df = self.book_db.books
        book = book_df[book_df["id"] == book_id]
        
        if book.empty:
            return None
        
        book_data = book.iloc[0].to_dict()
        
        # Добавляем отзывы
        book_data["reviews"] = self.get_book_reviews(book_id)
        
        # Добавляем статистику отзывов
        book_data["review_stats"] = self.get_review_stats(book_id)
        
        return book_data
    
    def get_book_reviews(self, book_id: int) -> List[Dict]:
        """Получение отзывов для книги"""
        book_reviews = self.reviews.get(str(book_id), [])
        
        # Добавляем демо-отзывы если нет настоящих
        if not book_reviews and book_id <= 20:  # для наших 20 книг
            demo_reviews = [
                {
                    "id": 1,
                    "username": "Читатель_1",
                    "rating": 5,
                    "text": "Отличная книга! Очень понравилось сочетание магии и повседневности.",
                    "date": "2023-10-15",
                    "likes": 12
                },
                {
                    "id": 2,
                    "username": "Критик_Профи",
                    "rating": 4,
                    "text": "Интересная концепция, но некоторые моменты можно было раскрыть лучше.",
                    "date": "2023-09-20",
                    "likes": 8
                },
                {
                    "id": 3,
                    "username": "Любитель_фэнтези",
                    "rating": 5,
                    "text": "Идеально для вечернего чтения! Уютная атмосфера и интересные персонажи.",
                    "date": "2023-11-05",
                    "likes": 15
                }
            ]
            book_reviews = demo_reviews
            self.reviews[str(book_id)] = demo_reviews
            self._save_reviews()
        
        return book_reviews
    
    def get_review_stats(self, book_id: int) -> Dict:
        """Получение статистики отзывов"""
        reviews = self.get_book_reviews(book_id)
        
        if not reviews:
            return {
                "average_rating": 0,
                "total_reviews": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        total_rating = sum(review["rating"] for review in reviews)
        average_rating = total_rating / len(reviews)
        
        # Распределение по оценкам
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating = review["rating"]
            if 1 <= rating <= 5:
                rating_dist[rating] += 1
        
        return {
            "average_rating": round(average_rating, 1),
            "total_reviews": len(reviews),
            "rating_distribution": rating_dist
        }
    
    def add_review(self, book_id: int, username: str, rating: int, text: str):
        """Добавление нового отзыва"""
        if str(book_id) not in self.reviews:
            self.reviews[str(book_id)] = []
        
        new_review = {
            "id": len(self.reviews[str(book_id)]) + 1,
            "username": username,
            "rating": rating,
            "text": text,
            "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "likes": 0
        }
        
        self.reviews[str(book_id)].append(new_review)
        self._save_reviews()
        return new_review
    
    def like_review(self, book_id: int, review_id: int):
        """Лайк отзыва"""
        book_reviews = self.reviews.get(str(book_id), [])
        for review in book_reviews:
            if review["id"] == review_id:
                review["likes"] = review.get("likes", 0) + 1
                self._save_reviews()
                return review["likes"]
        return None
    
    def show_book_page(self, book_id: int):
        """Отображение детальной страницы книги"""
        book_data = self.get_book_details(book_id)
        
        if not book_data:
            st.error("Книга не найдена")
            return
        
        # Кнопка "Назад"
        if st.button("← Назад к поиску"):
            st.session_state.current_page = "search"
            st.rerun()
        
        # Основная информация о книге
        st.markdown(f"# {book_data['title']}")
        st.markdown(f"### *{book_data['author']}*")
        
        # Обложка и основная информация
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Проверяем существование файла изображения
            cover_path = book_data.get("cover_image", "")
            if os.path.exists(cover_path) and os.path.isfile(cover_path):
                st.image(cover_path, width=200)
            else:
                # Заглушка если изображения нет
                st.markdown(f"""
                    <div style="width:200px; height:267px; background-color:#f0f0f0; 
                    display:flex; align-items:center; justify-content:center; 
                    border:1px solid #ddd; border-radius:5px; margin-bottom:20px;">
                    <div style="text-align:center; padding:10px;">
                    <span style="font-size:18px;">{book_data['main_genre']}</span><br>
                    <span style="font-size:14px;">Обложка</span>
                    </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Средний рейтинг
            avg_rating = book_data.get("rating", 0)
            st.markdown(f"**Рейтинг:** {avg_rating} ⭐")
            
            # Основные метрики
            st.metric("Год издания", book_data["year"])
            st.metric("Страниц", book_data["pages"])
        
        with col2:
            # Жанры
            st.markdown(f"**Жанр:** {book_data['main_genre']} → {book_data['sub_genre']}")
            
            # Детали
            if book_data.get("character_age") and book_data.get("character_profession"):
                st.markdown(f"**Главный герой:** {book_data['character_age']}, {book_data['character_profession']}")
            
            if book_data.get("setting_location") and book_data.get("setting_time_period"):
                st.markdown(f"**Сеттинг:** {book_data['setting_location']} ({book_data['setting_time_period']})")
            
            # Описание
            st.divider()
            st.subheader("📖 Описание")
            st.write(book_data["description"])
        
        # Теги и характеристики
        st.divider()
        st.subheader("🏷️ Теги и характеристики")
        
        # Создаем колонки для разных категорий тегов
        col_tags1, col_tags2, col_tags3 = st.columns(3)
        
        with col_tags1:
            if book_data.get("tags"):
                st.write("**Теги:**")
                for tag in book_data["tags"]:
                    st.markdown(f"`{tag}`")
        
        with col_tags2:
            if book_data.get("plot_tropes"):
                st.write("**Литературные тропы:**")
                for trope in book_data["plot_tropes"]:
                    st.markdown(f"› {trope}")
            
            if book_data.get("mood"):
                st.write("**Настроение:**")
                for mood in book_data["mood"]:
                    st.markdown(f"• {mood}")
        
        with col_tags3:
            if book_data.get("themes"):
                st.write("**Темы:**")
                for theme in book_data["themes"]:
                    st.markdown(f"▸ {theme}")
            
            if book_data.get("style"):
                st.write("**Стиль:**")
                for style in book_data["style"]:
                    st.markdown(f"▪ {style}")
            
            if book_data.get("pacing"):
                st.write(f"**Темп:** {book_data['pacing']}")
        
        # Отзывы и рецензии
        st.divider()
        st.subheader("💬 Отзывы и рецензии")
        
        # Статистика отзывов
        review_stats = book_data["review_stats"]
        
        if review_stats["total_reviews"] > 0:
            col_rev1, col_rev2, col_rev3 = st.columns(3)
            with col_rev1:
                st.metric("Средняя оценка", f"{review_stats['average_rating']} ⭐")
            with col_rev2:
                st.metric("Всего отзывов", review_stats["total_reviews"])
            with col_rev3:
                # Процент 5-звездочных отзывов
                five_star = review_stats["rating_distribution"].get(5, 0)
                if review_stats["total_reviews"] > 0:
                    percent_5star = (five_star / review_stats["total_reviews"]) * 100
                    st.metric("5⭐ отзывов", f"{percent_5star:.1f}%")
            
            # График распределения оценок
            st.write("**Распределение оценок:**")
            rating_data = pd.DataFrame({
                "Оценка": ["1⭐", "2⭐", "3⭐", "4⭐", "5⭐"],
                "Количество": [
                    review_stats["rating_distribution"].get(1, 0),
                    review_stats["rating_distribution"].get(2, 0),
                    review_stats["rating_distribution"].get(3, 0),
                    review_stats["rating_distribution"].get(4, 0),
                    review_stats["rating_distribution"].get(5, 0)
                ]
            })
            st.bar_chart(rating_data.set_index("Оценка"))
        else:
            st.info("У этой книги пока нет отзывов. Будьте первым!")
        
        # Список отзывов
        reviews = book_data["reviews"]
        if reviews:
            st.write(f"**Последние отзывы ({len(reviews)}):**")
            
            for review in reviews:
                with st.container():
                    # Создаем колонки для отзыва
                    col_review1, col_review2 = st.columns([1, 4])
                    
                    with col_review1:
                        # Рейтинг звездами
                        stars = "⭐" * review["rating"]
                        st.markdown(f"**{stars}**")
                        st.caption(f"{review['date']}")
                    
                    with col_review2:
                        st.markdown(f"**{review['username']}**")
                        st.write(review["text"])
                        
                        # Лайки
                        col_like1, col_like2 = st.columns([1, 5])
                        with col_like1:
                            if st.button(f"❤️ {review.get('likes', 0)}", 
                                       key=f"like_{book_id}_{review['id']}",
                                       use_container_width=True):
                                new_likes = self.like_review(book_id, review["id"])
                                st.rerun()
                    
                    st.divider()
        
        # Форма для добавления нового отзыва
        st.subheader("📝 Добавить отзыв")
        
        current_user = self.auth_manager.get_current_user()
        if current_user:
            with st.form(key=f"review_form_{book_id}"):
                col_rate1, col_rate2 = st.columns([1, 3])
                with col_rate1:
                    rating = st.selectbox("Оценка", options=[5, 4, 3, 2, 1], 
                                        format_func=lambda x: "⭐" * x)
                with col_rate2:
                    review_text = st.text_area("Текст отзыва", 
                                             placeholder="Поделитесь вашим мнением о книге...")
                
                submit = st.form_submit_button("Опубликовать отзыв")
                
                if submit and review_text:
                    self.add_review(book_id, current_user.username, rating, review_text)
                    st.success("Спасибо за ваш отзыв!")
                    st.rerun()
        else:
            st.info("Войдите в систему, чтобы оставить отзыв")