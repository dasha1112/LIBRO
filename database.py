import pandas as pd
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import streamlit as st

@dataclass
class Book:
    """Класс книги с расширенными атрибутами"""
    id: int
    title: str
    author: str
    main_genre: str
    sub_genre: str
    rating: float
    year: int
    pages: int
    description: str
    cover_image: str
    
    # Базовые атрибуты
    tags: List[str] = field(default_factory=list)
    
    # Детальные атрибуты (подтемы)
    character_age: Optional[str] = None
    character_profession: Optional[str] = None
    character_gender: Optional[str] = None
    
    setting_time_period: Optional[str] = None
    setting_location: Optional[str] = None
    setting_type: Optional[str] = None  # город, деревня, космос и т.д.
    
    plot_tropes: List[str] = field(default_factory=list)
    mood: List[str] = field(default_factory=list)
    pacing: Optional[str] = None  # медленный, средний, быстрый
    
    # Дополнительные категории
    themes: List[str] = field(default_factory=list)  # любовь, дружба, предательство
    style: List[str] = field(default_factory=list)   # поэтичный, простой, сложный

@dataclass
class Review:
    """Класс рецензии"""
    id: int
    book_id: int
    username: str
    rating: int
    text: str
    created_at: str
    likes: int = 0

class BookDatabase:
    """База данных книг и отзывов"""
    
    def __init__(self):
        self.books = self._create_sample_books()
        self.reviews = self._create_sample_reviews()
        self.user_lists = {}  # {username: {list_name: [book_ids]}}
    
    def _create_sample_books(self) -> pd.DataFrame:
        """Создание демонстрационной базы книг с иерархией жанров"""
        base_image_path = "images/"
        books_data = [
        {
            "id": 1,
            "title": "Мастер и Маргарита",
            "author": "Михаил Булгаков",
            "main_genre": "Классика",
            "sub_genre": "Магический реализм",
            "rating": 4.8,
            "year": 1966,
            "pages": 480,
            "description": "Жарким майским вечером председатель правления МАССОЛИТ Михаил Берлиоз и молодой поэт Иван Бездомный отправились на Патриаршие пруды, чтобы обсудить: существовал ли Иисус Христос. Беседой литераторов заинтересовался некий импозантный гражданин-иностранец. Профессор Воланд стал уверять новых знакомых, что лично присутствовал на допросе бродяги Иешуа Га-Ноцри, который проводил Понтий Пилат.\
            Александр Берлиоз и Иван Бездомный сочли собеседника сумасшедшим. А зря. Ведь через несколько часов Берлиоз попал под трамвай, а Иван отправился в сумасшедший дом, где и познакомился с мастером – возлюбленным Маргариты, будущей королевой бала у сатаны. Поэт узнает, что именно из-за романа о Понтии Пилате мастер оказался в сумасшедшем доме, а сама рукопись принесла писателю страшные несчастья…\
            Тем временем Воланд со свитой весьма необычным образом исследуют, как изменились москвичи за последние годы. Это исследование надолго останется в памяти тех, кому довелось столкнуться с происками дьявола и его помощников, обладающих специфическим чувством юмора и особым взглядом на справедливость и милосердие…",
            "cover_image": f"{base_image_path}book_1.png",
            "tags": ["мистика", "Москва", "дьявол", "любовь", "сатира"],
            "character_age": "30-40",
            "character_gender": "мужчина и женщина",
            "character_profession": "писатель",
            "setting_time_period": "1930-е годы",
            "setting_location": "Москва",
            "setting_type": "город",
            "plot_tropes": ["договор с дьяволом", "борьба добра и зла"],
            "mood": ["мистическое", "философское"],
            "pacing": "неравномерный",
            "themes": ["добро и зло", "творчество"],
            "style": ["сложный", "символический"]
        },
        {
            "id": 2,
            "title": "Сто лет одиночества",
            "author": "Габриэль Гарсия Маркес",
            "main_genre": "Классика",
            "sub_genre": "Магический реализм",
            "rating": 4.6,
            "year": 1967,
            "pages": 416,
            "description": "Сага о семье Буэндиа и магическом городе Макондо.",
            "cover_image": f"{base_image_path}book_2.jpg",
            "tags": ["семейная сага", "магия", "одиночество", "Латинская Америка"],
            "character_age": "разные",
            "character_gender": "мужчины и женщины",
            "character_profession": "разные",
            "setting_time_period": "XIX-XX века",
            "setting_location": "Колумбия",
            "setting_type": "изолированный город",
            "plot_tropes": ["семейная сага", "цикличность", "пророчество"],
            "mood": ["поэтическое", "мифическое"],
            "pacing": "плавный",
            "themes": ["одиночество", "время", "любовь"],
            "style": ["магический реализм", "поэтический"]
        },
        {
            "id": 3,
            "title": "Убийство в Восточном экспрессе",
            "author": "Агата Кристи",
            "main_genre": "Детектив",
            "sub_genre": "Классический детектив",
            "rating": 4.8,
            "year": 1934,
            "pages": 256,
            "description": "Эркюль Пуаро расследует убийство в застрявшем поезде.",
            "cover_image": f"{base_image_path}book_3.jpg",
            "tags": ["поезд", "убийство", "расследование", "Пуаро"],
            "character_age": "старше 40",
            "character_gender": "мужчина",
            "character_profession": "детектив",
            "setting_time_period": "1930-е годы",
            "setting_location": "Восточный экспресс",
            "setting_type": "поезд",
            "plot_tropes": ["закрытое пространство", "расследование"],
            "mood": ["интригующее", "логическое"],
            "pacing": "средний",
            "themes": ["правосудие", "логика", "преступление"],
            "style": ["классический", "детективный"]
        },
        {
            "id": 4,
            "title": "Десять негритят",
            "author": "Агата Кристи",
            "main_genre": "Детектив",
            "sub_genre": "Детектив-головоломка",
            "rating": 4.9,
            "year": 1939,
            "pages": 320,
            "description": "Десять незнакомцев приглашены на остров, где их начинают убивать по стишку.",
            "cover_image": f"{base_image_path}book_4.jpg",
            "tags": ["остров", "убийство", "тайна", "изоляция"],
            "character_age": "разные",
            "character_gender": "мужчины и женщины",
            "character_profession": "разные",
            "setting_time_period": "1930-е годы",
            "setting_location": "Остров",
            "setting_type": "изолированный остров",
            "plot_tropes": ["закрытое пространство", "поэтапные убийства"],
            "mood": ["зловещее", "параноидальное"],
            "pacing": "нарастающий",
            "themes": ["вина", "возмездие", "смерть"],
            "style": ["классический", "напряженный"]
        },
        {
            "id": 5,
            "title": "1984",
            "author": "Джордж Оруэлл",
            "main_genre": "Антиутопия",
            "sub_genre": "Политическая проза",
            "rating": 4.6,
            "year": 1949,
            "pages": 320,
            "description": "Жизнь под тотальным контролем Большого Брата в тоталитарном обществе.",
            "cover_image": f"{base_image_path}book_5.jpg",
            "tags": ["тоталитаризм", "контроль", "бунт", "будущее"],
            "character_age": "30-40",
            "character_gender": "мужчина",
            "character_profession": "госслужащий",
            "setting_time_period": "Будущее",
            "setting_location": "Лондон",
            "setting_type": "город-государство",
            "plot_tropes": ["тотальный контроль", "бунт личности"],
            "mood": ["мрачное", "тревожное"],
            "pacing": "напряженный",
            "themes": ["свобода и контроль", "истина и ложь"],
            "style": ["холодный", "аллегорический"]
        },
        {
            "id": 6,
            "title": "О дивный новый мир",
            "author": "Олдос Хаксли",
            "main_genre": "Антиутопия",
            "sub_genre": "Научная фантастика",
            "rating": 4.5,
            "year": 1932,
            "pages": 288,
            "description": "Идеальное будущее общество, где люди созданы в пробирках и лишены страданий.",
            "cover_image": f"{base_image_path}book_6.jpg",
            "tags": ["будущее", "генетика", "контроль", "удовольствие"],
            "character_age": "20-30",
            "character_gender": "мужчина",
            "character_profession": "специалист",
            "setting_time_period": "Будущее",
            "setting_location": "Лондон",
            "setting_type": "футуристическое общество",
            "plot_tropes": ["идеальное общество", "диссидент", "прогресс"],
            "mood": ["ироничное", "тревожное"],
            "pacing": "размеренный",
            "themes": ["свобода воли", "технологии", "счастье"],
            "style": ["сатирический", "философский"]
        },
        {
            "id": 7,
            "title": "Дюна",
            "author": "Фрэнк Герберт",
            "main_genre": "Фантастика",
            "sub_genre": "Планетарный роман",
            "rating": 4.7,
            "year": 1965,
            "pages": 704,
            "description": "Борьба за контроль над пустынной планетой, источником ценной пряности.",
            "cover_image": f"{base_image_path}book_7.jpg",
            "tags": ["космос", "политика", "пустыня", "мессия", "экология"],
            "character_age": "15-20",
            "character_gender": "мужчина",
            "character_profession": "наследник",
            "setting_time_period": "Далекое будущее",
            "setting_location": "Планета Арракис",
            "setting_type": "пустынная планета",
            "plot_tropes": ["мессианский сюжет", "политический заговор"],
            "mood": ["эпическое", "философское"],
            "pacing": "медленный",
            "themes": ["власть и религия", "экология", "судьба"],
            "style": ["эпический", "политический"]
        },
        {
            "id": 8,
            "title": "Автостопом по галактике",
            "author": "Дуглас Адамс",
            "main_genre": "Фантастика",
            "sub_genre": "Космическая комедия",
            "rating": 4.7,
            "year": 1979,
            "pages": 224,
            "description": "Землянин Артур Дент путешествует по галактике после уничтожения Земли.",
            "cover_image": f"{base_image_path}book_8.jpg",
            "tags": ["космос", "комедия", "путешествия", "абсурд"],
            "character_age": "20-30",
            "character_gender": "мужчина",
            "character_profession": "низший клерк",
            "setting_time_period": "Настоящее и будущее",
            "setting_location": "Космос",
            "setting_type": "космические корабли",
            "plot_tropes": ["неудачливый герой", "космические приключения"],
            "mood": ["абсурдное", "ироничное"],
            "pacing": "быстрый",
            "themes": ["абсурдность бытия", "технологии", "дружба"],
            "style": ["ироничный", "абсурдистский"]
        },
        {
            "id": 9,
            "title": "Гарри Поттер и философский камень",
            "author": "Джоан Роулинг",
            "main_genre": "Фэнтези",
            "sub_genre": "Героическое фэнтези",
            "rating": 4.9,
            "year": 1997,
            "pages": 400,
            "description": "Мальчик-сирота узнает, что он волшебник, и поступает в школу магии.",
            "cover_image": f"{base_image_path}book_9.jpg",
            "tags": ["волшебство", "школа", "дружба", "сирота"],
            "character_age": "младше 20",
            "character_gender": "мужчина",
            "character_profession": "ученик",
            "setting_time_period": "1990-е годы",
            "setting_location": "Хогвартс",
            "setting_type": "магическая школа",
            "plot_tropes": ["избранный герой", "тайное происхождение"],
            "mood": ["приключенческое", "чудесное"],
            "pacing": "динамичный",
            "themes": ["добро против зла", "дружба", "взросление"],
            "style": ["увлекательный", "детальный"]
        },
        {
            "id": 10,
            "title": "Властелин колец: Братство кольца",
            "author": "Дж. Р. Р. Толкин",
            "main_genre": "Фэнтези",
            "sub_genre": "Эпическое фэнтези",
            "rating": 4.9,
            "year": 1954,
            "pages": 432,
            "description": "Хоббит Фродо должен уничтожить Кольцо Всевластья в жерле Роковой Горы.",
            "cover_image": f"{base_image_path}book_10.png",
            "tags": ["кольцо", "путешествие", "битвы", "Средиземье"],
            "character_age": "разные",
            "character_gender": "мужчина",
            "character_profession": "хоббит",
            "setting_time_period": "Мифическое прошлое",
            "setting_location": "Средиземье",
            "setting_type": "вымышленный мир",
            "plot_tropes": ["опасное путешествие", "битва добра и зла"],
            "mood": ["эпическое", "героическое", "мрачное"],
            "pacing": "медленный",
            "themes": ["дружба", "жертва", "власть", "война"],
            "style": ["эпический", "мифологический"]
        },
        {
            "id": 11,
            "title": "Три товарища",
            "author": "Эрих Мария Ремарк",
            "main_genre": "Классика",
            "sub_genre": "Военная проза",
            "rating": 4.7,
            "year": 1936,
            "pages": 480,
            "description": "Дружба и любовь трех бывших солдат в послевоенной Германии.",
            "cover_image": f"{base_image_path}book_11.jpg",
            "tags": ["дружба", "любовь", "потеря", "война", "Германия"],
            "character_age": "30-35",
            "character_gender": "мужчина",
            "character_profession": "автомеханик",
            "setting_time_period": "1920-е годы",
            "setting_location": "Германия",
            "setting_type": "город",
            "plot_tropes": ["верная дружба", "любовь после потерь"],
            "mood": ["меланхолическое", "трогательное"],
            "pacing": "размеренный",
            "themes": ["посттравматический синдром", "верность"],
            "style": ["лиричный", "психологический"]
        },
        {
            "id": 12,
            "title": "Над пропастью во ржи",
            "author": "Джером Д. Сэлинджер",
            "main_genre": "Классика",
            "sub_genre": "Роман воспитания",
            "rating": 4.3,
            "year": 1951,
            "pages": 240,
            "description": "Несколько дней из жизни подростка Холдена Колфилда, сбежавшего из школы.",
            "cover_image": f"{base_image_path}book_12.jpg",
            "tags": ["подросток", "бунт", "одиночество", "Нью-Йорк"],
            "character_age": "младше 20",
            "character_gender": "мужчина",
            "character_profession": "школьник",
            "setting_time_period": "1940-е годы",
            "setting_location": "Нью-Йорк",
            "setting_type": "город",
            "plot_tropes": ["бунт подростка", "поиск себя"],
            "mood": ["бунтарское", "одинокое"],
            "pacing": "средний",
            "themes": ["взросление", "лицемерие", "изоляция"],
            "style": ["исповедальный", "разговорный"]
        },
        {
            "id": 13,
            "title": "Портрет Дориана Грея",
            "author": "Оскар Уайльд",
            "main_genre": "Классика",
            "sub_genre": "Философский роман",
            "rating": 4.6,
            "year": 1890,
            "pages": 320,
            "description": "Молодой красавец продает душу за вечную молодость, а его портрет стареет вместо него.",
            "cover_image": f"{base_image_path}book_13.jpg",
            "tags": ["красота", "разврат", "портрет", "договор", "Лондон"],
            "character_age": "20-30",
            "character_gender": "мужчина",
            "character_profession": "аристократ",
            "setting_time_period": "Викторианская эпоха",
            "setting_location": "Лондон",
            "setting_type": "город",
            "plot_tropes": ["договор с дьяволом", "двойник", "падение"],
            "mood": ["декадентское", "мрачное", "эстетское"],
            "pacing": "средний",
            "themes": ["красота и разложение", "мораль", "искусство"],
            "style": ["эстетский", "афористичный"]
        },
        {
            "id": 14,
            "title": "Метро 2033",
            "author": "Дмитрий Глуховский",
            "main_genre": "Постапокалипсис",
            "sub_genre": "Научная фантастика",
            "rating": 4.5,
            "year": 2005,
            "pages": 384,
            "description": "Молодой человек путешествует по станциям московского метро после ядерной войны.",
            "cover_image": f"{base_image_path}book_14.jpg",
            "tags": ["постапокалипсис", "метро", "мутанты", "Москва"],
            "character_age": "20-30",
            "character_gender": "мужчина",
            "character_profession": "военный",
            "setting_time_period": "Близкое будущее",
            "setting_location": "Москва",
            "setting_type": "метро",
            "plot_tropes": ["путешествие героя", "выживание"],
            "mood": ["мрачное", "гнетущее"],
            "pacing": "напряженный",
            "themes": ["выживание", "страх", "человечность"],
            "style": ["атмосферный", "жесткий"]
        },
        {
            "id": 15,
            "title": "Старик и море",
            "author": "Эрнест Хемингуэй",
            "main_genre": "Классика",
            "sub_genre": "Повесть",
            "rating": 4.4,
            "year": 1952,
            "pages": 128,
            "description": "Старый рыбак вступает в схватку с огромной рыбой в открытом море.",
            "cover_image": f"{base_image_path}book_15.jpg",
            "tags": ["рыбак", "море", "борьба", "одиночество", "Куба"],
            "character_age": "старше 40",
            "character_gender": "мужчина",
            "character_profession": "рыбак",
            "setting_time_period": "1940-е годы",
            "setting_location": "Куба",
            "setting_type": "море",
            "plot_tropes": ["борьба с природой", "нравственная победа"],
            "mood": ["суровое", "философское"],
            "pacing": "медленный",
            "themes": ["человек и природа", "упорство", "достоинство"],
            "style": ["лаконичный", "символический"]
        },
        {
            "id": 16,
            "title": "Анна Каренина",
            "author": "Лев Толстой",
            "main_genre": "Классика",
            "sub_genre": "Роман",
            "rating": 4.7,
            "year": 1877,
            "pages": 864,
            "description": "Трагическая история любви замужней аристократки Анны Карениной к офицеру Вронскому.",
            "cover_image": f"{base_image_path}book_16.png",
            "tags": ["любовь", "измена", "общество", "трагедия", "Россия"],
            "character_age": "20-30",
            "character_gender": "женщина",
            "character_profession": "аристократка",
            "setting_time_period": "XIX век",
            "setting_location": "Россия",
            "setting_type": "город и деревня",
            "plot_tropes": ["любовный треугольник", "падение женщины"],
            "mood": ["трагическое", "драматическое"],
            "pacing": "размеренный",
            "themes": ["любовь и долг", "семья", "общество"],
            "style": ["психологический", "реалистичный"]
        },
        {
            "id": 17,
            "title": "Улисс",
            "author": "Джеймс Джойс",
            "main_genre": "Модернизм",
            "sub_genre": "Роман",
            "rating": 4.2,
            "year": 1922,
            "pages": 730,
            "description": "Один день из жизни Леопольда Блума в Дублине, рассказанный через поток сознания.",
            "cover_image": f"{base_image_path}book_17.jpg",
            "tags": ["Дублин", "один день", "сознание", "сложный"],
            "character_age": "30-40",
            "character_gender": "мужчина",
            "character_profession": "агент по рекламе",
            "setting_time_period": "1904 год",
            "setting_location": "Дублин",
            "setting_type": "город",
            "plot_tropes": ["один день жизни", "аллюзии"],
            "mood": ["абсурдное", "рефлексивное"],
            "pacing": "медленный",
            "themes": ["обыденность", "память", "искусство"],
            "style": ["поток сознания", "экспериментальный"]
        },
        {
            "id": 18,
            "title": "Шерлок Холмс. Собака Баскервилей",
            "author": "Артур Конан Дойл",
            "main_genre": "Детектив",
            "sub_genre": "Классический детектив",
            "rating": 4.8,
            "year": 1902,
            "pages": 256,
            "description": "Холмс расследует смерть баронета, в которой подозревают собаку-призрака.",
            "cover_image": f"{base_image_path}book_18.jpg",
            "tags": ["Холмс", "расследование", "призрак", "деревня"],
            "character_age": "старше 40",
            "character_gender": "мужчина",
            "character_profession": "частный детектив",
            "setting_time_period": "Викторианская эпоха",
            "setting_location": "Англия",
            "setting_type": "сельская местность",
            "plot_tropes": ["семейное проклятие", "расследование"],
            "mood": ["загадочное", "готическое"],
            "pacing": "средний",
            "themes": ["логика против суеверий", "наследство"],
            "style": ["классический", "атмосферный"]
        },
        {
            "id": 19,
            "title": "Колыбель для кошки",
            "author": "Курт Воннегут",
            "main_genre": "Научная фантастика",
            "sub_genre": "Сатира",
            "rating": 4.4,
            "year": 1963,
            "pages": 288,
            "description": "Сатира о создании опасного вещества «лед-девять» и конце света.",
            "cover_image": f"{base_image_path}book_19.jpg",
            "tags": ["сатира", "конец света", "наука", "религия"],
            "character_age": "30-40",
            "character_gender": "мужчина",
            "character_profession": "журналист",
            "setting_time_period": "Холодная война",
            "setting_location": "Вымышленная страна",
            "setting_type": "островное государство",
            "plot_tropes": ["опасное изобретение", "сатира на общество"],
            "mood": ["ироничное", "циничное", "абсурдное"],
            "pacing": "быстрый",
            "themes": ["наука и мораль", "религия", "абсурд войны"],
            "style": ["сатирический", "черный юмор"]
        },
        {
            "id": 20,
            "title": "Атлант расправил плечи",
            "author": "Айн Рэнд",
            "main_genre": "Философский роман",
            "sub_genre": "Антиутопия",
            "rating": 4.5,
            "year": 1957,
            "pages": 1168,
            "description": "Промышленники и творцы объявляют забастовку против общества, живущего за их счет.",
            "cover_image": f"{base_image_path}book_20.jpg",
            "tags": ["капитализм", "индивидуализм", "забастовка", "антиутопия", "бизнес"],
            "character_age": "30-50",
            "character_gender": "мужчины и женщины",
            "character_profession": "промышленники",
            "setting_time_period": "1950-е годы",
            "setting_location": "США",
            "setting_type": "индустриальное",
            "plot_tropes": ["забастовка гениев", "крушение системы"],
            "mood": ["дидактическое", "интеллектуальное"],
            "pacing": "медленный",
            "themes": ["индивидуализм", "разум", "свобода"],
            "style": ["риторический", "идейный"]
        }
    ]
    
        return pd.DataFrame(books_data)
    
    def _create_sample_reviews(self) -> pd.DataFrame:
        """Создание демонстрационных отзывов"""
        reviews_data = [
            {
                "id": 1,
                "book_id": 1,
                "username": "Читатель_1",
                "rating": 5,
                "text": "Уютная и вдохновляющая книга! Идеально для вечернего чтения.",
                "created_at": "2023-10-15",
                "likes": 12
            },
            {
                "id": 2,
                "book_id": 2,
                "username": "Любитель_фэнтези",
                "rating": 4,
                "text": "Отличное сочетание исторического детектива и фэнтези.",
                "created_at": "2023-09-20",
                "likes": 8
            }
        ]
        return pd.DataFrame(reviews_data)
    
    def get_filter_options(self) -> Dict:
        """Получение всех доступных опций для фильтрации"""
        books_df = self.books
        
        return {
            "main_genres": sorted(books_df["main_genre"].unique()),
            "sub_genres": sorted(books_df["sub_genre"].dropna().unique()),
            "character_ages": sorted(books_df["character_age"].dropna().unique()),
            "character_professions": sorted(books_df["character_profession"].dropna().unique()),
            "settings": sorted(books_df["setting_location"].dropna().unique()),
            "time_periods": sorted(books_df["setting_time_period"].dropna().unique()),
            "moods": sorted(set([m for moods in books_df["mood"] for m in moods])),
            "tropes": sorted(set([t for tropes in books_df["plot_tropes"] for t in tropes]))
        }
    
    def get_reviews_for_user(self, username: str) -> pd.DataFrame:
        """Получение отзывов пользователя"""
        return self.reviews[self.reviews["username"] == username]