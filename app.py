import streamlit as st
import pandas as pd
import os
from auth import UserManager
from database import BookDatabase
from book_filter import BookFilter
from user_lists import UserListsManager
from book_page import BookPageManager
from simple_recommender import SimpleRecommender

# Настройка страницы
st.set_page_config(
    page_title="LIBRO",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': "https://github.com",
        'About': "LIBRO - веб-приложение для поиска книг"
    }
)

# Инициализация менеджеров
@st.cache_resource
def init_managers():
    """Инициализация всех менеджеров"""
    return {
        "auth": UserManager(),
        "db": BookDatabase(),
        "lists": UserListsManager(),
        "book_page": None,  # Инициализируем позже
        "recommender": None
    }

managers = init_managers()
auth_manager = managers["auth"]
db = managers["db"]
lists_manager = managers["lists"]

# Инициализируем BookPageManager после создания других менеджеров
if managers["book_page"] is None:
    managers["book_page"] = BookPageManager(db, auth_manager, lists_manager)
book_page_manager = managers["book_page"]

# Инициализируем SimpleRecommender
if managers["recommender"] is None:
    managers["recommender"] = SimpleRecommender(db, book_page_manager)
recommender = managers["recommender"]

# CSS стили
st.markdown("""
    <style>
    /* Уменьшаем заголовки */
    h1 {
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        margin-top: 0.5rem !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
    }
    
    /* Улучшаем карточки книг */
    .book-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .book-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Улучшаем кнопки */
    .stButton > button {
        border-radius: 5px;
        font-weight: 500;
    }
    
    /* Стили для вкладок */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 20px;
        font-weight: 500;
    }
    
    /* Убираем верхний отступ */
    .main .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Функции отображения
def show_login_register():
    """Отображение формы входа/регистрации"""
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Имя пользователя")
            password = st.text_input("Пароль", type="password")
            submit = st.form_submit_button("Войти")
            
            if submit:
                success, message = auth_manager.login(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Имя пользователя")
            email = st.text_input("Email")
            new_password = st.text_input("Пароль", type="password")
            confirm_password = st.text_input("Подтвердите пароль", type="password")
            submit = st.form_submit_button("Зарегистрироваться")
            
            if submit:
                if new_password != confirm_password:
                    st.error("Пароли не совпадают")
                else:
                    success, message = auth_manager.register(new_username, email, new_password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

def show_book_card(book, show_actions=True):
    """Отображение карточки книги"""
    with st.container():
        # Создаем контейнер для заголовка с возможностью клика
        col_title1, col_title2 = st.columns([5, 1])
        
        with col_title1:
            # Используем Markdown для стилизации заголовка
            st.markdown(f"### {book['title']}")
            st.markdown(f"*{book['author']}*")
        
        with col_title2:
            # Кнопка для перехода на страницу книги
            if st.button("📖 Подробнее", 
                       key=f"details_btn_{book['id']}",
                       help="Перейти на страницу книги",
                       use_container_width=True):
                st.session_state.current_page = "book_details"
                st.session_state.selected_book_id = book["id"]
                st.rerun()
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Проверяем существование файла изображения
            import os
            cover_path = book.get("cover_image", "")
            
            if os.path.exists(cover_path) and os.path.isfile(cover_path):
                st.image(cover_path, width=120)
            else:
                # Заглушка если изображения нет
                st.markdown(f"""
                    <div style="width:120px; height:160px; background-color:#f0f0f0; 
                    display:flex; align-items:center; justify-content:center; 
                    border:1px solid #ddd; border-radius:5px; margin-bottom:10px;">
                    <div style="text-align:center; padding:10px;">
                    <span style="font-size:14px;">{book['main_genre'][:10]}</span><br>
                    <span style="font-size:12px;">ID: {book['id']}</span>
                    </div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Основная информация
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("Рейтинг", f"{book['rating']}⭐")
            with col_info2:
                st.metric("Год", book["year"])
            with col_info3:
                st.metric("Страниц", book["pages"])
            
            # Жанры
            st.write(f"**{book['main_genre']}** → {book['sub_genre']}")
            
            # Детали
            if pd.notna(book["character_age"]) and pd.notna(book["character_profession"]):
                st.write(f"**Герой:** {book['character_age']}, {book['character_profession']}")
            
            if pd.notna(book["setting_location"]) and pd.notna(book["setting_time_period"]):
                st.write(f"**Место:** {book['setting_location']} ({book['setting_time_period']})")
            
            # Теги
            if book.get("tags"):
                tags_html = " ".join([f'<span style="background:#f0f0f0; padding:2px 8px; border-radius:10px; margin:2px; display:inline-block;">{tag}</span>' for tag in book["tags"]])
                st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
        
        # Действия с книгой (добавление в списки)
        if show_actions and auth_manager.get_current_user():
            user = auth_manager.get_current_user()
            user_lists = lists_manager.get_user_lists(user.username)
            
            # Кнопки для добавления в списки
            st.write("**Добавить в список:**")
            col_actions = st.columns(5)
            list_names = ["Читаю", "Прочитано", "Планирую", "Брошено", "Любимые"]
            list_mapping = {
                "Читаю": "reading",
                "Прочитано": "read", 
                "Планирую": "planned",
                "Брошено": "dropped",
                "Любимые": "favorites"
            }
            
            for i, list_name in enumerate(list_names):
                with col_actions[i]:
                    list_key = list_mapping[list_name]
                    is_in_list = book["id"] in user_lists[list_key].book_ids
                    button_text = f"✓ {list_name}" if is_in_list else list_name
                    button_type = "primary" if is_in_list else "secondary"
                    
                    if st.button(button_text, 
                               key=f"list_{book['id']}_{list_key}",
                               type=button_type,
                               use_container_width=True):
                        if is_in_list:
                            lists_manager.remove_book_from_list(
                                user.username,
                                list_key,
                                book["id"]
                            )
                        else:
                            lists_manager.add_book_to_list(
                                user.username,
                                list_key,
                                book["id"]
                            )
                        st.rerun()
        
        st.divider()

def show_book_details_page():
    """Отображение детальной страницы книги"""
    book_id = st.session_state.get("selected_book_id")
    if not book_id:
        st.error("Книга не выбрана")
        return
    
    book_page_manager.show_book_page(book_id)

def show_user_profile():
    """Отображение профиля пользователя"""
    user = auth_manager.get_current_user()
    
    if not user:
        return
    
    st.subheader("👤 Мой профиль")
    
    # Статистика
    user_lists = lists_manager.get_user_lists(user.username)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Прочитано", len(user_lists["read"].book_ids))
    with col2:
        st.metric("Читаю сейчас", len(user_lists["reading"].book_ids))
    with col3:
        st.metric("В планах", len(user_lists["planned"].book_ids))
    with col4:
        st.metric("Любимые", len(user_lists["favorites"].book_ids))
    
    # Списки книг
    st.subheader("📋 Мои списки")
    
    # Маппинг вкладок на ключи списков
    tabs_config = [
        ("Читаю", "reading"),
        ("Прочитано", "read"),
        ("Планирую", "planned"),
        ("Брошено", "dropped"),
        ("Любимые", "favorites"),
        ("Рецензии", "reviews")
    ]
    
    tabs = st.tabs([name for name, _ in tabs_config])
    
    for i, (tab_name, list_key) in enumerate(tabs_config):
        with tabs[i]:
            if list_key != "reviews":
                books = lists_manager.get_books_in_list(user.username, list_key, db)
                if books:
                    for book in books:
                        show_book_card(book, show_actions=False)
                else:
                    st.info(f"Вы еще не добавили книги в список '{tab_name}'")
            else:
                with tabs[5]:  # Рецензии
                # Получаем отзывы из book_page_manager
                    user_reviews = db.get_user_reviews_from_manager(user.username, book_page_manager)
                    
                    if not user_reviews.empty:
                        # Статистика
                        total_reviews = len(user_reviews)
                        avg_rating = user_reviews['rating'].mean() if total_reviews > 0 else 0
                        
                        col_stats1, col_stats2 = st.columns(2)
                        with col_stats1:
                            st.metric("Всего отзывов", total_reviews)
                        with col_stats2:
                            st.metric("Средняя оценка", f"{avg_rating:.1f} ⭐")
                        
                        st.divider()
                        
                        # Сортировка
                        col_sort1, col_sort2 = st.columns(2)
                        with col_sort1:
                            sort_by = st.selectbox(
                                "Сортировать по:",
                                ["Дате (новые)", "Дате (старые)", "Оценке (высокие)", "Оценке (низкие)", "Лайкам"],
                                key="reviews_sort"
                            )
                        
                        # Применяем сортировку
                        if sort_by == "Дате (новые)":
                            user_reviews = user_reviews.sort_values('created_at', ascending=False)
                        elif sort_by == "Дате (старые)":
                            user_reviews = user_reviews.sort_values('created_at', ascending=True)
                        elif sort_by == "Оценке (высокие)":
                            user_reviews = user_reviews.sort_values('rating', ascending=False)
                        elif sort_by == "Оценке (низкие)":
                            user_reviews = user_reviews.sort_values('rating', ascending=True)
                        elif sort_by == "Лайкам":
                            user_reviews = user_reviews.sort_values('likes', ascending=False)
                        
                        # Отображение отзывов
                        for _, review in user_reviews.iterrows():
                            with st.container():
                                # Карточка отзыва
                                col_rev1, col_rev2, col_rev3 = st.columns([1, 4, 1])
                                
                                with col_rev1:
                                    # Обложка книги (если есть)
                                    book_info = db.books[db.books["id"] == review['book_id']]
                                    if not book_info.empty and 'cover_image' in book_info.columns:
                                        cover_path = book_info.iloc[0]['cover_image']
                                        if os.path.exists(cover_path):
                                            st.image(cover_path, width=80)
                                
                                with col_rev2:
                                    # Информация о книге
                                    book_title = review.get('book_title', f"Книга ID: {review['book_id']}")
                                    book_author = review.get('book_author', "")
                                    
                                    # Кликабельная ссылка на книгу
                                    if st.button(f"**{book_title}**", 
                                            key=f"book_link_{review['book_id']}_{review['id']}",
                                            help="Перейти к книге"):
                                        st.session_state.current_page = "book_details"
                                        st.session_state.selected_book_id = review['book_id']
                                        st.rerun()
                                    
                                    if book_author:
                                        st.caption(f"*{book_author}*")
                                    
                                    # Оценка
                                    stars = "⭐" * review['rating']
                                    st.write(f"**Оценка:** {stars}")
                                    
                                    # Текст отзыва
                                    with st.expander("Показать отзыв", expanded=True):
                                        st.write(review["text"])
                                    
                                    # Дата и лайки
                                    col_meta1, col_meta2 = st.columns(2)
                                    with col_meta1:
                                        st.caption(f"📅 {review['created_at']}")
                                    with col_meta2:
                                        st.caption(f"❤️ {review.get('likes', 0)}")
                                
                                with col_rev3:
                                    # Действия
                                    if st.button("✏️", 
                                            key=f"edit_{review['book_id']}_{review['id']}",
                                            help="Редактировать"):
                                        st.session_state.editing_review = review['id']
                                        st.session_state.editing_book_id = review['book_id']
                                        st.rerun()
                                    
                                    if st.button("🗑️", 
                                            key=f"delete_{review['book_id']}_{review['id']}",
                                            help="Удалить",
                                            type="secondary"):
                                        # Здесь будет логика удаления
                                        st.info("Для удаления отзыва перейдите на страницу книги")
                                
                                st.divider()
                    else:
                        # Если отзывов нет
                        st.info("📝 Вы еще не написали ни одной рецензии")
                        
                        st.markdown("""
                        ### Как оставить отзыв?
                        
                        1. **Найдите книгу** через поиск вверху страницы
                        2. **Перейдите на страницу книги**, нажав "📖 Подробнее"
                        3. **Пролистайте вниз** до раздела "💬 Отзывы и рецензии"
                        4. **Заполните форму** "📝 Добавить отзыв"
                        
                        Ваши отзывы помогут другим читателям выбрать книгу!
                        """)

def show_recommendations_page():
    """Отображение страницы с рекомендациями"""
    user = auth_manager.get_current_user()
    if not user:
        st.error("Войдите в систему для просмотра рекомендаций")
        return
    
    st.header("🎯 Рекомендуемое вам")
    
    # 1. Собираем ВСЕ книги пользователя из всех списков
    user_all_books = set()  # ID всех книг пользователя
    
    # Все категории списков
    list_categories = ["reading", "read", "planned", "dropped", "favorites"]
    
    for category in list_categories:
        books_in_list = lists_manager.get_books_in_list(user.username, category, db)
        for book in books_in_list:
            if isinstance(book, dict) and "id" in book:
                user_all_books.add(book["id"])
    
    # 2. Получаем ID книг с хорошими отзывами, исключая те, что уже в списках
    good_reviews_books = []
    for book_id_str, reviews in book_page_manager.reviews.items():
        for review in reviews:
            if review["username"] == user.username and review["rating"] >= 4:
                book_id = int(book_id_str)
                if book_id not in user_all_books:  # Исключаем если уже в списках
                    good_reviews_books.append(book_id)
    
    if not good_reviews_books:
        # Показываем популярные книги, которых нет в списках пользователя
        popular = db.books[
            ~db.books["id"].isin(user_all_books)  # Исключаем книги из списков
        ].sort_values("rating", ascending=False).head(10)
        
        if not popular.empty:
            for _, book in popular.iterrows():
                show_book_card(book, show_actions=True)
        return
    
    # 3. Находим похожие книги, учитывая теги и тропы
    recommended_ids = set()
    all_recommendations = []
    
    for good_book_id in good_reviews_books[:3]:  # Берем только 3 книги для анализа
        good_book = db.books[db.books["id"] == good_book_id]
        if good_book.empty:
            continue
        
        good_book = good_book.iloc[0]
        
        # Получаем теги и тропы из хорошей книги
        good_book_tags = set(good_book.get("tags", [])) if isinstance(good_book.get("tags"), list) else set()
        good_book_tropes = set(good_book.get("plot_tropes", [])) if isinstance(good_book.get("plot_tropes"), list) else set()
        good_book_moods = set(good_book.get("mood", [])) if isinstance(good_book.get("mood"), list) else set()
        
        # Ищем похожие книги
        similar_books = []
        
        for _, book in db.books.iterrows():
            # Пропускаем если книга уже в списках пользователя
            if book["id"] in user_all_books:
                continue
            
            # Пропускаем если уже в рекомендациях
            if book["id"] in recommended_ids:
                continue
            
            # Пропускаем если это та же книга
            if book["id"] == good_book_id:
                continue
            
            similarity_score = 0
            
            # Совпадение по жанру
            if book["main_genre"] == good_book["main_genre"]:
                similarity_score += 2
            
            # Совпадение по поджанру
            if book["sub_genre"] == good_book["sub_genre"]:
                similarity_score += 1
            
            # Совпадение по тегам
            book_tags = set(book.get("tags", [])) if isinstance(book.get("tags"), list) else set()
            common_tags = good_book_tags.intersection(book_tags)
            similarity_score += len(common_tags) * 0.5
            
            # Совпадение по тропам
            book_tropes = set(book.get("plot_tropes", [])) if isinstance(book.get("plot_tropes"), list) else set()
            common_tropes = good_book_tropes.intersection(book_tropes)
            similarity_score += len(common_tropes) * 0.5
            
            # Совпадение по настроению
            book_moods = set(book.get("mood", [])) if isinstance(book.get("mood"), list) else set()
            common_moods = good_book_moods.intersection(book_moods)
            similarity_score += len(common_moods) * 0.3
            
            # Бонус за высокий рейтинг
            if book["rating"] >= 4.0:
                similarity_score += 0.5
            
            if similarity_score > 0:
                similar_books.append({
                    "book": book,
                    "score": similarity_score,
                    "common_tags": list(common_tags),
                    "common_tropes": list(common_tropes),
                    "common_moods": list(common_moods)
                })
        
        # Сортируем по схожести и берем топ
        similar_books.sort(key=lambda x: x["score"], reverse=True)
        
        for item in similar_books[:4]:  # Берем до 4 книг от каждой исходной
            if item["book"]["id"] not in recommended_ids:
                all_recommendations.append(item)
                recommended_ids.add(item["book"]["id"])
    
    # 4. Если мало рекомендаций, добавляем книги по другим критериям
    if len(all_recommendations) < 5:
        # Ищем книги с общими тегами/тропами из ВСЕХ оцененных книг
        all_good_tags = set()
        all_good_tropes = set()
        all_good_moods = set()
        
        for good_book_id in good_reviews_books[:5]:
            good_book = db.books[db.books["id"] == good_book_id]
            if not good_book.empty:
                book = good_book.iloc[0]
                if isinstance(book.get("tags"), list):
                    all_good_tags.update(book["tags"])
                if isinstance(book.get("plot_tropes"), list):
                    all_good_tropes.update(book["plot_tropes"])
                if isinstance(book.get("mood"), list):
                    all_good_moods.update(book["mood"])
        
        # Ищем книги с общими тегами/тропами
        for _, book in db.books.iterrows():
            if (book["id"] in user_all_books) or (book["id"] in recommended_ids):
                continue
            
            book_tags = set(book.get("tags", [])) if isinstance(book.get("tags"), list) else set()
            book_tropes = set(book.get("plot_tropes", [])) if isinstance(book.get("plot_tropes"), list) else set()
            book_moods = set(book.get("mood", [])) if isinstance(book.get("mood"), list) else set()
            
            common_with_all_tags = all_good_tags.intersection(book_tags)
            common_with_all_tropes = all_good_tropes.intersection(book_tropes)
            common_with_all_moods = all_good_moods.intersection(book_moods)
            
            if common_with_all_tags or common_with_all_tropes or common_with_all_moods:
                all_recommendations.append({
                    "book": book,
                    "score": 1.0,
                    "common_tags": list(common_with_all_tags),
                    "common_tropes": list(common_with_all_tropes),
                    "common_moods": list(common_with_all_moods)
                })
                recommended_ids.add(book["id"])
                
            if len(all_recommendations) >= 10:  # Максимум 10 рекомендаций
                break
    
    # 5. Сортируем и показываем рекомендации
    if all_recommendations:
        # Сортируем по score
        all_recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        st.write(f"**Основываясь на ваших оценках, вам могут понравиться ({len(all_recommendations)} книг):**")
        
        for item in all_recommendations:
            book = item["book"]
            
            # Создаем подсказку почему рекомендовано
            reasons = []
            if item.get("common_tags"):
                reasons.append(f"Теги: {', '.join(item['common_tags'][:2])}")
            if item.get("common_tropes"):
                reasons.append(f"Тропы: {', '.join(item['common_tropes'][:2])}")
            if item.get("common_moods"):
                reasons.append(f"Настроение: {', '.join(item['common_moods'][:1])}")
            
            if reasons:
                st.info(f"**Почему:** {' | '.join(reasons)}")
            
            show_book_card(book, show_actions=True)
    else:
        st.info("""
        Не удалось найти рекомендации на основе ваших оценок.
        
        **Возможные причины:**
        1. Вы уже добавили в списки большинство похожих книг
        2. Попробуйте оценить книги разных жанров и стилей
        3. Или посмотрите популярные книги:
        """)
        
        # Показываем популярные книги, которых нет в списках
        popular = db.books[
            ~db.books["id"].isin(user_all_books)
        ].sort_values("rating", ascending=False).head(10)
        
        if not popular.empty:
            for _, book in popular.iterrows():
                show_book_card(book, show_actions=True)

def show_main_search():
    """Главная страница поиска"""
    # Инициализация фильтра
    if "book_filter" not in st.session_state:
        st.session_state.book_filter = BookFilter(db.books)
    
    book_filter = st.session_state.book_filter
    
    # Боковая панель с фильтрами
    with st.sidebar:
        st.header("🔍 Фильтры поиска")
        
        # Основной жанр
        main_genre = st.selectbox(
            "Основной жанр",
            options=["Все"] + book_filter.filter_hierarchy["main_genre"]["options"],
            key="main_genre"
        )
        
        selected_filters = {}
        if main_genre != "Все":
            selected_filters["main_genre"] = main_genre
        
        # Обновляем опции фильтров
        book_filter.update_filter_options(selected_filters)
        
        # Поджанр (появляется только если выбран основной жанр)
        if main_genre != "Все":
            sub_genre_options = ["Все"] + book_filter.filter_hierarchy["sub_genre"]["options"]
            sub_genre = st.selectbox(
                "Поджанр",
                options=sub_genre_options,
                key="sub_genre"
            )
            
            if sub_genre != "Все":
                selected_filters["sub_genre"] = sub_genre
                book_filter.update_filter_options(selected_filters)
        
        # Разворачиваемые секции для подтем
        with st.expander("👤 Характеристики героя", expanded=False):
            # Пол героя
            if book_filter.filter_hierarchy["character"]["children"]["character_gender"]["options"]:
                character_gender = st.selectbox(
                    "Пол героя",
                    options=["Любой"] + book_filter.filter_hierarchy["character"]["children"]["character_gender"]["options"],
                    key="character_gender"
                )
                if character_gender != "Любой":
                    selected_filters["character_gender"] = character_gender
            
            # Слайдер для диапазона возраста
            if book_filter.filter_hierarchy["character"]["children"]["character_age"]["options"]:
                age_options = book_filter.filter_hierarchy["character"]["children"]["character_age"]["options"]
                
                if age_options:  # Проверяем, что список не пустой
                    # Определяем min и max из доступных опций
                    min_age_val = min(age_options)
                    max_age_val = max(age_options)
                    
                    # Устанавливаем дефолтные значения (20-40 как вы хотели)
                    default_min = max(20, min_age_val)
                    default_max = min(40, max_age_val)
                    
                    st.write("**Возраст героя:**")
                    
                    # Инициализируем состояние для слайдера, если его нет
                    if "character_age_range" not in st.session_state:
                        st.session_state.character_age_range = (default_min, default_max)
                    
                    # Слайдер для выбора диапазона
                    age_range = st.slider(
                        "Диапазон возраста (лет)",
                        min_value=min_age_val,
                        max_value=max_age_val,
                        value=st.session_state.character_age_range,
                        step=5,
                        key="character_age_range_slider",
                        label_visibility="collapsed",
                        help="Выберите минимальный и максимальный возраст героя"
                    )
                    
                    # Обновляем состояние
                    st.session_state.character_age_range = age_range
                    
                    # Показываем выбранный диапазон
                    col_age1, col_age2 = st.columns(2)
                    with col_age1:
                        st.caption(f"От: **{age_range[0]}** лет")
                    with col_age2:
                        st.caption(f"До: **{age_range[1]}** лет")
                    
                    # Добавляем в фильтры только если выбрано не всё
                    if age_range != (min_age_val, max_age_val):
                        selected_filters["character_age_range"] = age_range
                else:
                    st.info("Нет доступных вариантов возраста для выбранных фильтров")
            
            # Профессия героя
            if book_filter.filter_hierarchy["character"]["children"]["character_profession"]["options"]:
                character_profession = st.selectbox(
                    "Профессия героя",
                    options=["Любая"] + book_filter.filter_hierarchy["character"]["children"]["character_profession"]["options"],
                    key="character_profession"
                )
                if character_profession != "Любая":
                    selected_filters["character_profession"] = character_profession
        
        with st.expander("🌍 Сеттинг", expanded=False):
            if book_filter.filter_hierarchy["setting"]["children"]["setting_location"]["options"]:
                setting_location = st.selectbox(
                    "Место действия",
                    options=["Любое"] + book_filter.filter_hierarchy["setting"]["children"]["setting_location"]["options"],
                    key="setting_location"
                )
                if setting_location != "Любое":
                    selected_filters["setting_location"] = setting_location
            
            if book_filter.filter_hierarchy["setting"]["children"]["setting_time_period"]["options"]:
                setting_time = st.selectbox(
                    "Временной период",
                    options=["Любой"] + book_filter.filter_hierarchy["setting"]["children"]["setting_time_period"]["options"],
                    key="setting_time_period"
                )
                if setting_time != "Любой":
                    selected_filters["setting_time_period"] = setting_time
        
        with st.expander("📖 Сюжет и атмосфера", expanded=False):
            if book_filter.filter_hierarchy["plot"]["children"]["plot_tropes"]["options"]:
                plot_tropes = st.multiselect(
                    "Литературные тропы",
                    options=book_filter.filter_hierarchy["plot"]["children"]["plot_tropes"]["options"],
                    key="plot_tropes"
                )
                if plot_tropes:
                    selected_filters["plot_tropes"] = plot_tropes
            
            if book_filter.filter_hierarchy["plot"]["children"]["mood"]["options"]:
                mood = st.multiselect(
                    "Настроение",
                    options=book_filter.filter_hierarchy["plot"]["children"]["mood"]["options"],
                    key="mood"
                )
                if mood:
                    selected_filters["mood"] = mood
        
        # Фильтр по рейтингу
        st.divider()
        st.subheader("⭐ Рейтинг")
        
        rating_options = [
            "Любой рейтинг",
            "Больше 4.8 ⭐⭐⭐⭐⭐",
            "Больше 4.5 ⭐⭐⭐⭐", 
            "Больше 4.0 ⭐⭐⭐⭐",
            "Больше 3.5 ⭐⭐⭐",
            "Больше 3.0 ⭐⭐⭐",
            "Больше 2.0 ⭐⭐",
            "Больше 1.0 ⭐"
        ]
        
        rating_mapping = {
            "Любой рейтинг": 0.0,
            "Больше 4.8 ⭐⭐⭐⭐⭐": 4.8,
            "Больше 4.5 ⭐⭐⭐⭐": 4.5,
            "Больше 4.0 ⭐⭐⭐⭐": 4.0,
            "Больше 3.5 ⭐⭐⭐": 3.5,
            "Больше 3.0 ⭐⭐⭐": 3.0,
            "Больше 2.0 ⭐⭐": 2.0,
            "Больше 1.0 ⭐": 1.0
        }
        
        selected_rating_text = st.selectbox(
            "Минимальный рейтинг",
            options=rating_options,
            index=0,
            key="min_rating_select"
        )
        
        if selected_rating_text != "Любой рейтинг":
            selected_filters["min_rating"] = rating_mapping[selected_rating_text]
        
        # Кнопки
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Применить фильтры", type="primary", use_container_width=True):
                st.session_state.current_filters = selected_filters
                st.rerun()
        with col2:
            if st.button("🗑️ Сбросить", type="secondary", use_container_width=True):
                # Сбрасываем все состояния фильтров
                for key in list(st.session_state.keys()):
                    if key.startswith(("main_genre", "sub_genre", "character", "setting", "plot", "min_rating", "character_age_range")):
                        del st.session_state[key]
                if "current_filters" in st.session_state:
                    del st.session_state.current_filters
                st.rerun()
    
    # Основная область
    st.markdown("<h1>LIBRO 📚</h1>", unsafe_allow_html=True)
    st.caption("Найди свою следующую любимую книгу")
    
    # Применение фильтров
    current_filters = st.session_state.get("current_filters", {})
    filtered_books = book_filter.apply_filters(current_filters)
    
    # Отображение результатов
    st.subheader(f"📖 Найдено книг: {len(filtered_books)}")
    
    if len(current_filters) > 0:
        filter_desc = book_filter.get_filter_description(current_filters)
        
        # Добавляем рейтинг в описание если выбран
        if "min_rating" in current_filters:
            filter_desc += f" | Рейтинг: >{current_filters['min_rating']}"
        
        st.info(f"**Примененные фильтры:** {filter_desc}")
    
    if len(filtered_books) == 0:
        st.warning("Книги по вашим критериям не найдены. Попробуйте изменить фильтры.")
    else:
        # Статистика
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Средний рейтинг", f"{filtered_books['rating'].mean():.1f}⭐")
        with col2:
            st.metric("Жанров", len(filtered_books['main_genre'].unique()))
        with col3:
            st.metric("Авторов", len(filtered_books['author'].unique()))
        with col4:
            st.metric("Лет издания", f"{filtered_books['year'].min()}-{filtered_books['year'].max()}")
        
        st.divider()
        
        # Список книг
        for _, book in filtered_books.iterrows():
            show_book_card(book)

# Главное приложение
def main():
    # Инициализация состояния навигации
    if "current_page" not in st.session_state:
        st.session_state.current_page = "search"
    
    if "selected_book_id" not in st.session_state:
        st.session_state.selected_book_id = None
    
    # Проверка авторизации
    current_user = auth_manager.get_current_user()
    
    if not current_user:
        # Показываем форму входа/регистрации
        st.markdown("<h1>LIBRO 📚</h1>", unsafe_allow_html=True)
        st.caption("Добро пожаловать! Войдите или зарегистрируйтесь")
        show_login_register()
    else:
        # Простая навигация через st.radio
        st.markdown(f"**Привет, {current_user.username}!**")

        # Создаем горизонтальную навигацию
        nav_options = ["🔍 Поиск", "🎯 Рекомендации", "👤 Профиль"]
        nav_page_map = {
            "🔍 Поиск": "search",
            "🎯 Рекомендации": "recommendations", 
            "👤 Профиль": "profile"
        }

        # Определяем текущий выбор
        current_nav = next(
            (key for key, value in nav_page_map.items() if value == st.session_state.current_page),
            "🔍 Поиск"
        )

        # Создаем навигацию
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔍 Поиск", use_container_width=True, 
                        type="primary" if st.session_state.current_page == "search" else "secondary"):
                st.session_state.current_page = "search"
                st.rerun()

        with col2:
            if st.button("🎯 Рекомендации", use_container_width=True,
                        type="primary" if st.session_state.current_page == "recommendations" else "secondary"):
                st.session_state.current_page = "recommendations"
                st.rerun()

        with col3:
            if st.button("👤 Профиль", use_container_width=True,
                        type="primary" if st.session_state.current_page == "profile" else "secondary"):
                st.session_state.current_page = "profile"
                st.rerun()
        
        # Отображение текущей страницы
        if st.session_state.current_page == "search":
            show_main_search()
        elif st.session_state.current_page == "book_details":
            show_book_details_page()
        elif st.session_state.current_page == "profile":
            show_user_profile()
        elif st.session_state.current_page == "recommendations":
            show_recommendations_page()

if __name__ == "__main__":
    main()