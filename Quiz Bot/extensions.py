import json


# Основной класс для работы с базой данных.
class DataBase:
    def __init__(self):
        self.users = self.load_data("users.json")           # Список пользователей.
        self.questions = self.load_data("questions.json")   # Список вопросов.
        self.questions_count = len(self.questions)          # Количество вопросов.

    # Загружаем данные пользователя.
    @staticmethod
    def load_data(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        return data

    # Сохраняем данные пользователя.
    @staticmethod
    def save_data(data, file_name):
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file)

    # Сами данные пользователя.
    def get_user(self, chat_id):
        for user in self.users:
            if user["chat_id"] == chat_id:
                return user
        user = {
            "chat_id": chat_id,
            "is_passing": False,
            "is_passed": False,
            "question_index": None,
            "answers": []
        }
        self.users.append(user)
        self.save_data(self.users, "users.json")
        return user

    # Обновляем данные пользователя.
    def set_user(self, chat_id, update):
        for user in self.users:
            if user["chat_id"] == chat_id:
                user.update(update)
                self.save_data(self.users, "users.json")
                return

    # Получаем индекс текущего вопроса.
    def get_question(self, index):
        if 0 <= index < len(self.questions):
            return self.questions[index]
        return None

    # Загружаем данные для алгоритма "взвешивания". Счётчик
    @staticmethod
    def load_comparison(filename="comparison_animal.json"):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        return data

    # Загружаем данные для алгоритма "взвешивания". Условие
    @staticmethod
    def load_condition(filename="condition_animal.json"):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        return data
