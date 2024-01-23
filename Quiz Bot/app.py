import telebot
import os
import logging
import json

from dotenv import load_dotenv
from extensions import DataBase

# Проанализирует файл .env, а затем загрузит все найденные переменные как переменные среды.
load_dotenv()

# Загружаем токен.
bot = telebot.TeleBot(os.getenv("TOKEN"))


# Загружаем основной класс в переменную.
db = DataBase()


@bot.message_handler(commands=["start"])
def start(message):
    user = db.get_user(message.chat.id)
    if user["chat_id"]:
        text = (f"✌️Приветствую вас, {message.chat.first_name}✌️.\n\n🐘🐯🐻\nЯ бот-викторина от Московского зоопарка! "
                f"Я рад приветствовать тебя на своей площадке. У меня для тебя подготовлена увлекательная "
                f"викторина, по прохождении который ты узнаешь своё тотемное животное. И программа опеки.\n\n"
                f"Присоединяйся и проведи время с пользой и удовольствием!\n\n"
                f"Основное меню доступно по комманде: /menu\n🐘🐯🐻")
        markup = telebot.types.InlineKeyboardMarkup()
        butt_1 = telebot.types.InlineKeyboardButton("⭐ Пройти викторину ⭐", callback_data="quiz")
        markup.add(butt_1)
        # Показываем картинку и прикреп. текст.
        bot.send_photo(message.chat.id, open("pictures/Start.jpg", 'rb'), caption=text, reply_markup=markup)


@bot.message_handler(commands=["menu"])
def show_menu(message):
    user = db.get_user(message.chat.id)
    if user["chat_id"]:
        bot.delete_message(message.chat.id, message.message_id - 1)
        text = "Добро пожаловать! Вы попали в основное меню:"
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        quizz = telebot.types.InlineKeyboardButton("⭐ Пройти викторину ⭐", callback_data="quiz")
        revi = telebot.types.InlineKeyboardButton("💬 Оставить отзыв 💬", callback_data="review")
        contact = telebot.types.InlineKeyboardButton("☎️ Контакты ☎️", callback_data="contact")
        reset = telebot.types.InlineKeyboardButton("🔁 Сбросить данные 🔁", callback_data="resets")
        guardian = telebot.types.InlineKeyboardButton("Стать опекуном",
                                                      url="https://moscowzoo.ru/my-zoo/become-a-guardian/")
        markup.add(quizz, revi, contact, reset, guardian)
        bot.send_message(message.chat.id, text, reply_markup=markup)


# Обрабатываем нажатие на кнопку Пройти викторину.
@bot.callback_query_handler(func=lambda query: query.data == "quiz")
def start_passing(query):
    user = db.get_user(query.message.chat.id)
    # Если пользователь уже прошел эту викторину.
    if user["is_passed"]:
        bot.send_message(query.message.chat.id, "Вы уже проходили эту викторину. Рад видеть вас снова 😉")
        db.set_user(user["chat_id"], {"is_passed": False, "is_passing": False, "question_index": None,
                                      "answers": []})

    # Если нет то, даём ему её пройти.
    if user["is_passing"]:
        return

    db.set_user(query.message.chat.id, {"question_index": 0, "is_passing": True})
    user = db.get_user(query.message.chat.id)
    post = get_question_message(user)
    # Отправляем сообщение.
    if post is not None:
        bot.send_message(query.message.chat.id, post["text"], reply_markup=post["keyboard"])


# Обрабатываем нажатие на кнопку ответы.
@bot.callback_query_handler(func=lambda query: query.data.startswith("?ans"))
def answered(query):
    user = db.get_user(query.message.chat.id)
    if user["is_passed"] or not user["is_passing"]:
        return
    answer_index = int(query.data.split("&")[1])
    user["answers"].append(answer_index)
    db.set_user(query.message.chat.id, {"answers": user["answers"]})
    post = get_answered_message(user)
    if post is not None:
        bot.edit_message_text(post["text"], query.message.chat.id, query.message.id, reply_markup=post["keyboard"])


# Обрабатываем нажатие на кнопку след. вопрос.
@bot.callback_query_handler(func=lambda query: query.data == "?next")
def next_question(query):
    user = db.get_user(query.message.chat.id)
    if user["is_passed"] or not user["is_passing"]:
        return
    user["question_index"] += 1
    db.set_user(query.message.chat.id, {"question_index": user["question_index"]})
    post = get_question_message(user)
    if post is not None:
        bot.edit_message_text(post["text"], query.message.chat.id, query.message.id, reply_markup=post["keyboard"])


# Обрабатываем нажатие на кнопку Оставить отзыв.
@bot.callback_query_handler(func=lambda query: query.data == "review")
def send_comment(query):
    bot.send_message(query.message.chat.id, f"✌️Привет! {query.message.chat.first_name}✌️\n\n"
                                            f"Я ценю мнение каждого пользователя. Если у тебя есть несколько минут, "
                                            f"чтобы поделиться своим мнением обо мне, "
                                            f"я был бы безмерно благодарен!\n"
                                            f"Твой отзыв поможет мне стать ещё лучше! Спасибо!")
    bot.register_next_step_handler(query.message, save_reviews)


# Обрабатываем нажатие на кнопку Сброс данных.
@bot.callback_query_handler(func=lambda query: query.data == "resets")
def reset_user(query):
    text = "❗ Учтите что, сброс данных обнулит все, в том числе и результат викторины! ❗\nВы уверены?"
    markup = telebot.types.InlineKeyboardMarkup()
    yes = telebot.types.InlineKeyboardButton("✅ Да ✅", callback_data="yes")
    no = telebot.types.InlineKeyboardButton("❌ Нет❌ ", callback_data="no")
    markup.add(yes, no)
    bot.send_message(query.message.chat.id, text, reply_markup=markup)


# Обрабатываем нажатие на кнопку Контакты.
@bot.callback_query_handler(func=lambda query: query.data == "contact")
def contacts(query):
    user = db.get_user(query.message.chat.id)
    if user["chat_id"]:
        text = "Мы в социальных сетях:\n\nTelegram: @Moscowzoo_official\nVK: vk.com/moscow_zoo\n"\
               "OK: ok.ru/moscowzoo\n\nЧтобы вернуться в меню: /menu"
        markup = telebot.types.InlineKeyboardMarkup()
        html = telebot.types.InlineKeyboardButton("Наш сайт", url="https://moscowzoo.ru/")
        markup.add(html)
        bot.send_message(query.message.chat.id, text, reply_markup=markup)


# Функция обработки конца и след. вопроса викторины.
def get_question_message(user):
    if user["question_index"] == db.questions_count:
        animal_counts = db.load_comparison()
        animal_data = db.load_condition()
        question_data = json.load(open("questions.json", encoding="utf-8"))

        for question_index, answer_index in enumerate(user["answers"]):
            animal_id = question_data[question_index]["answers"][answer_index]["id"]
            animal_counts[animal_id] += 1

        max_animal = max(animal_counts, key=animal_counts.get)
        animal_info = animal_data.get(max_animal)
        if animal_info:
            animal = animal_info[0]
            filename = animal_info[1]
            text = (f"Привет! Поздравляю тебя с успешным прохождением викторины! "
                    f"Позволь мне предложить тебе замечательное животное, которое, как мне кажется, "
                    f"подходит именно тебе. Твоё тотемное животное - {animal}\n\nЧтобы вернуться в меню: /menu")

            db.set_user(user["chat_id"], {"is_passed": True, "is_passing": False})

            markup = telebot.types.InlineKeyboardMarkup()
            butt_1 = telebot.types.InlineKeyboardButton("↪ Попробовать ещё раз? ↩", callback_data="quiz")
            markup.add(butt_1)
            bot.send_photo(user["chat_id"], open(filename, 'rb'), caption=text, reply_markup=markup)

            bot.send_message(user["chat_id"], "Теперь немного о программе опеки. программа «Возьми животное "
                                              "под опеку» — это ваш личный вклад в дело сохранения биоразнообразия "
                                              "Земли и развитие нашего зоопарка. Основная задача Московского зоопарка "
                                              "с самого начала его существования это — сохранение биоразнообразия "
                                              "нашей планеты. Когда вы берете под опеку животное, вы помогаете нам в "
                                              "этом благородном деле. Чтобы подробнее ознакомиться с программой, "
                                              "предлагаю вам перейти по ссылке - "
                                              "https://moscowzoo.ru/my-zoo/become-a-guardian/"
                                              "\n\nЧтобы вернуться в меню: /menu")

            result = f"ID: {user['chat_id']}. Прошел викторину успешно. его тотемное животное: {animal}"
            bot.send_message(chat_id=os.getenv("SUPPORT_CHAT_ID"), text=result)

    question = db.get_question(user["question_index"])
    if question is None:
        return
    keyboard = telebot.types.InlineKeyboardMarkup()
    for answer_index, answer in enumerate(question["answers"]):
        keyboard.row(telebot.types.InlineKeyboardButton(f"{chr(answer_index + 97)}) {answer['text']}",
                                                        callback_data=f"?ans&{answer_index}"))
    text = f"🔹 Вопрос №{user['question_index'] + 1} 🔹\n\n{question['text']}"
    return {
        "text": text,
        "keyboard": keyboard
    }


# Функция обработки выбора ответов.
def get_answered_message(user):
    question = db.get_question(user["question_index"])
    text = f"🔹 Вопрос №{user['question_index'] + 1} 🔹\n\n{question['text']}\n"
    for answer_index, answer in enumerate(question["answers"]):
        text += f"{chr(answer_index + 97)}) {answer['text']}"
        if answer_index == user["answers"]:
            text += " ❌"
        elif answer_index == user["answers"][-1]:
            text += " ✅"
        text += "\n"
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton("▶ Далее ▶", callback_data="?next"))
    return {
        "text": text,
        "keyboard": keyboard
    }


@bot.callback_query_handler(func=lambda query: query.data == "yes" or query.data == "no")
def input_yes(query):
    if query.data == "yes":
        user = db.get_user(query.message.chat.id)
        db.set_user(user["chat_id"], {"is_passed": False, "is_passing": False, "question_index": 0,
                                      "answers": []})
        bot.send_message(query.message.chat.id, "✅ Сброс данных успешно выполнился! ✅\nЧтобы вернуться в меню: /menu")
    elif query.data == "no":
        bot.send_message(query.message.chat.id, "❌ Вы отказались! ❌\nЧтобы вернуться в меню: /menu")


# Функция сохранения отзыва.
def save_reviews(message):
    text = message.text
    user = message.from_user.username
    forbidden_chars = ["!", "@", "#", "$", "%"]         # Символы, с которых нельзя начать текст.
    if not text:
        bot.reply_to(message, "❗ Ошибка! Вы не указали текст отзыва ❗")
        return
    elif len(text) > 500:
        bot.reply_to(message, "❗ Ошибка! Слишком много символов в тексте! Текст не должен превышать 500 символов ❗")
        return
    elif text.startswith(tuple(forbidden_chars)):
        bot.reply_to(message, "❗ Ошибка! Начало текста не может начинаться с символов! ❗")
        return
    else:
        bot.delete_message(message.chat.id, message.message_id - 1)
        with open("reviews.txt", "a+", encoding="utf-8") as file:
            file.write(f"Отзыв от {user}:\n{text}\n\n")
        bot.reply_to(message, "🙏 Спасибо за твой отзыв! 🙏\nЧтобы вернуться в меню: /menu")


if __name__ == "__main__":
    # логирование
    logging.basicConfig(
        handlers=[logging.FileHandler(filename="logs.txt", encoding='utf-8', mode='a+')],
        format="%(asctime)s %(name)s : %(levelname)s : %(message)s", datefmt="%F %A %T", level=logging.DEBUG)

    # Запускаем бота.
    try:
        bot.polling(none_stop=True)
        logging.debug("Бот запущен!")
    except Exception as e:
        logging.error(f"Неудалось запустить бота! Причина: {e}")
        raise e
