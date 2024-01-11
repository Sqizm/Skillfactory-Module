import requests
import json     # Для парсинга полученных ответов используем библиотеку JSON.
from config import keys, API_KEY


# При ошибке пользователя
# (например, введена неправильная или несуществующая валюта или неправильно введено число)
# вызываем собственное написанное исключение APIException с текстом пояснения ошибки.
class APIException(Exception):
    pass


# Для отправки запросов к API описываем класс со статическим методом get_price(),
# который принимает три аргумента и возвращает нужную сумму в валюте.
class APIrequests:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        if quote == base:
            raise APIException("Ошибка: Невозможно перевести одинаковые валюты.")

        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise APIException(f"Ошибка: Не удалось обработать валюту '{quote}'")

        try:
            base_ticker = keys[base]
        except KeyError:
            raise APIException(f"Ошибка: Не удалось обработать валюту '{base}'")

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f"Ошибка: Не удалось обработать количество '{amount}'")

        # Для получения курса валют необходимо использовать любое удобное API
        # и отправлять к нему запросы с помощью библиотеки Requests.
        r = requests.get(f'https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{quote_ticker}/{base_ticker}/{amount}')
        total_base = json.loads(r.content)
        return total_base
