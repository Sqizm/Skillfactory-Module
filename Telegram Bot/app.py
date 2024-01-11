import telebot
from config import keys, TOKEN    # 11. Токен Telegram-бота и API Key храниться в специальном конфиге.
from extensions import APIException, APIrequests    # 12. Все классы спрятаны в файле extensions.py.

bot = telebot.TeleBot(TOKEN)


# При вводе команды /start или /help пользователю выводятся инструкции по применению бота.
@bot.message_handler(commands=["start", "help"])
def send_welcome(message: telebot.types.Message):
    # Игнорируем ошибку PEP 8: E128, иначе некорректно будет ввыводиться текст в боте.
    text = (f"Привет, {message.chat.first_name}\n\n"
"Чтобы начать конвертировать волюту, введите команду боту в следующем формате:\n\n"
"<имя валюты>  <в какую валюту нужно перевести>"
"  <количество переводимой валюты>\n\nПример: рубль доллар 2\n\n"
"Список всех доступных валют:  /values")
    bot.reply_to(message, text)


# При вводе команды /values будет выводиться информация о всех доступных валютах в читаемом виде.
@bot.message_handler(commands=["values"])
def values(message: telebot.types.Message):
    text = "Доступные валюты:\n"
    for key in keys.keys():
        text = "\n".join((text, key))
    bot.reply_to(message, text)


@bot.message_handler(content_types=["text", ])
def convert(message: telebot.types.Message):
    # Текст любой ошибки с указанием типа ошибки выводится пользователю в сообщения.
    try:
        value = message.text.split(' ')

        if len(value) != 3:
            raise APIException("Неверный формат параметров.")

        quote, base, amount = value
        total_base = APIrequests.get_price(quote, base, amount)
    except APIException as e:
        bot.reply_to(message, f"Вы ошиблись.\n{e}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: Неудалось обработать команду:\n{e}")
    else:
        text = f"Цена {amount} {quote} в {base} - {total_base['conversion_result']}"
        bot.send_message(message.chat.id, text)


bot.polling()
