import pandas as pd
from typing import Dict, List, Optional

class BookFilter:
    """Класс для фильтрации книг с иерархией фильтров"""
    
    def __init__(self, books_df: pd.DataFrame):
        self.books_df = books_df.copy()
        self.current_filters = {}
        self.filter_hierarchy = self._create_filter_hierarchy()
    
    def _create_filter_hierarchy(self) -> Dict:
        """Создание иерархии фильтров"""
        return {
            "main_genre": {
                "label": "Основной жанр",
                "type": "select",
                "options": sorted(self.books_df["main_genre"].unique()),
                "dependencies": {}
            },
            "sub_genre": {
                "label": "Поджанр",
                "type": "select",
                "options": [],
                "dependencies": ["main_genre"]
            },
            "character": {
                "label": "Характеристики героя",
                "type": "group",
                "children": {
                    "character_age": {
                        "label": "Возраст героя",
                        "type": "select",
                        "options": []
                    },
                    "character_gender": {
                        "label": "Пол героя",
                        "type": "select",
                        "options": []
                    },
                    "character_profession": {
                        "label": "Профессия героя",
                        "type": "select",
                        "options": []
                    }
                }
            },
            "setting": {
                "label": "Сеттинг",
                "type": "group",
                "children": {
                    "setting_location": {
                        "label": "Место действия",
                        "type": "select",
                        "options": []
                    },
                    "setting_time_period": {
                        "label": "Временной период",
                        "type": "select",
                        "options": []
                    }
                }
            },
            "plot": {
                "label": "Сюжет и атмосфера",
                "type": "group",
                "children": {
                    "plot_tropes": {
                        "label": "Литературные тропы",
                        "type": "multiselect",
                        "options": []
                    },
                    "mood": {
                        "label": "Настроение",
                        "type": "multiselect",
                        "options": []
                    },
                    "pacing": {
                        "label": "Темп повествования",
                        "type": "select",
                        "options": ["медленный", "средний", "быстрый"]
                    }
                }
            }
        }
    
    def update_filter_options(self, selected_filters: Dict):
        """Обновление доступных опций фильтров на основе выбранных значений"""
        filtered_df = self.books_df.copy()
        
        # Применяем уже выбранные фильтры
        for key, value in selected_filters.items():
            if value and key in filtered_df.columns:
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[key].apply(
                        lambda x: any(v in (x if isinstance(x, list) else []) for v in value)
                    )]
                else:
                    filtered_df = filtered_df[filtered_df[key] == value]
        
        # Обновляем опции для зависимых фильтров
        if "main_genre" in selected_filters and selected_filters["main_genre"]:
            self.filter_hierarchy["sub_genre"]["options"] = sorted(
                filtered_df["sub_genre"].dropna().unique()
            )
        
        # Обновляем опции для характеристик героя
        character_df = filtered_df[["character_age", "character_gender", "character_profession"]].dropna()
        self.filter_hierarchy["character"]["children"]["character_age"]["options"] = sorted(
            character_df["character_age"].unique()
        )
        self.filter_hierarchy["character"]["children"]["character_gender"]["options"] = sorted(
            character_df["character_gender"].unique()
        )
        self.filter_hierarchy["character"]["children"]["character_profession"]["options"] = sorted(
            character_df["character_profession"].unique()
        )
        
        # Обновляем опции для сеттинга
        setting_df = filtered_df[["setting_location", "setting_time_period"]].dropna()
        self.filter_hierarchy["setting"]["children"]["setting_location"]["options"] = sorted(
            setting_df["setting_location"].unique()
        )
        self.filter_hierarchy["setting"]["children"]["setting_time_period"]["options"] = sorted(
            setting_df["setting_time_period"].unique()
        )
        
        # Обновляем опции для сюжета
        all_tropes = set()
        all_moods = set()
        
        for tropes in filtered_df["plot_tropes"]:
            if isinstance(tropes, list):
                all_tropes.update(tropes)
        
        for moods in filtered_df["mood"]:
            if isinstance(moods, list):
                all_moods.update(moods)
        
        self.filter_hierarchy["plot"]["children"]["plot_tropes"]["options"] = sorted(all_tropes)
        self.filter_hierarchy["plot"]["children"]["mood"]["options"] = sorted(all_moods)
    
    def apply_filters(self, filters: Dict) -> pd.DataFrame:
        """Применение фильтров к данным"""
        filtered_df = self.books_df.copy()
        
        for key, value in filters.items():
            if value:
                if key == "min_rating":  # Особый случай для минимального рейтинга
                    filtered_df = filtered_df[filtered_df["rating"] >= value]
                elif isinstance(value, list) and value:
                    if key in ["plot_tropes", "mood", "tags", "themes", "style"]:
                        # Для списковых полей
                        filtered_df = filtered_df[filtered_df[key].apply(
                            lambda x: any(v in (x if isinstance(x, list) else []) for v in value)
                        )]
                    else:
                        filtered_df = filtered_df[filtered_df[key].isin(value)]
                elif not isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[key] == value]
        
        return filtered_df
    
    def get_filter_description(self, filters: Dict) -> str:
        """Получение текстового описания примененных фильтров"""
        descriptions = []
        
        if filters.get("main_genre"):
            descriptions.append(f"Жанр: {filters['main_genre']}")
        
        if filters.get("sub_genre"):
            descriptions.append(f"Поджанр: {filters['sub_genre']}")
        
        if filters.get("character_age"):
            descriptions.append(f"Возраст героя: {filters['character_age']}")
        
        if filters.get("character_profession"):
            descriptions.append(f"Профессия: {filters['character_profession']}")
        
        if filters.get("setting_location"):
            descriptions.append(f"Место: {filters['setting_location']}")
        
        # Обрабатываем min_rating отдельно
        if "min_rating" in filters:
            # Этот фильтр не добавляем в общее описание, так как он обрабатывается отдельно в app.py
            pass
        
        return " | ".join(descriptions)