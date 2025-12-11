import streamlit as st
import pandas as pd
from auth import UserManager
from database import BookDatabase
from book_filter import BookFilter
from user_lists import UserListsManager
from book_page import BookPageManager

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
        "book_page": None  # Инициализируем позже
    }

managers = init_managers()
auth_manager = managers["auth"]
db = managers["db"]
lists_manager = managers["lists"]

# Инициализируем BookPageManager после создания других менеджеров
if managers["book_page"] is None:
    managers["book_page"] = BookPageManager(db, auth_manager, lists_manager)
book_page_manager = managers["book_page"]

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
                # Вкладка с рецензиями
                user_reviews = db.get_reviews_for_user(user.username)
                if not user_reviews.empty:
                    for _, review in user_reviews.iterrows():
                        with st.container():
                            # Найдем книгу для отображения названия
                            book = db.books[db.books["id"] == review["book_id"]]
                            if not book.empty:
                                book_title = book.iloc[0]["title"]
                                st.write(f"**Книга:** {book_title}")
                            st.write(f"**Оценка:** {'⭐' * review['rating']}")
                            st.write(f"**Текст:** {review['text']}")
                            st.write(f"*{review['created_at']}*")
                            st.divider()
                else:
                    st.info("Вы еще не написали ни одной рецензии")

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
            if book_filter.filter_hierarchy["character"]["children"]["character_age"]["options"]:
                character_age = st.selectbox(
                    "Возраст героя",
                    options=["Любой"] + book_filter.filter_hierarchy["character"]["children"]["character_age"]["options"],
                    key="character_age"
                )
                if character_age != "Любой":
                    selected_filters["character_age"] = character_age
            
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
        
        # Фильтр по рейтингу (исправленный)
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
                for key in list(st.session_state.keys()):
                    if key.startswith(("main_genre", "sub_genre", "character", "setting", "plot", "min_rating", "year_range")):
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
        
        # Добавляем год в описание
        if "year_min" in current_filters and "year_max" in current_filters:
            filter_desc += f" | Год: {current_filters['year_min']}-{current_filters['year_max']}"
        
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
        # Верхняя панель с пользователем и навигацией
        col_nav1, col_nav2, col_nav3 = st.columns([6, 1, 1])
        
        with col_nav1:
            st.caption(f"Привет, {current_user.username}!")
        
        with col_nav2:
            # Кнопка для перехода к поиску
            if st.session_state.current_page != "search":
                if st.button("🔍 Поиск", use_container_width=True):
                    st.session_state.current_page = "search"
                    st.rerun()
        
        with col_nav3:
            if st.button("👤 Профиль", use_container_width=True):
                st.session_state.current_page = "profile"
                st.rerun()
        
        # Отображение текущей страницы
        if st.session_state.current_page == "search":
            show_main_search()
        elif st.session_state.current_page == "book_details":
            show_book_details_page()
        elif st.session_state.current_page == "profile":
            show_user_profile()

if __name__ == "__main__":
    main()