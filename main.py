import telebot
from telebot import types
from config import BOT_TOKEN
from db import DBManager
from api import GigaChatAPI


bot = telebot.TeleBot(BOT_TOKEN)
db = DBManager()
gigachat = GigaChatAPI()

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👤 Мой профиль")
    btn2 = types.KeyboardButton("📌 Добавить данные")
    btn3 = types.KeyboardButton("⭐ Мои интересы")
    btn4 = types.KeyboardButton("❓ Вопрос–Ответ")
    btn5 = types.KeyboardButton("🎯 Выбрать профессию")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "👋 Привет! Это FutureMe - бот помощник в выборе профессии.\n\n"
        "📌 Используй кнопки ниже для работы."
        "Версия: beta 3"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())


@bot.message_handler(func=lambda m: m.text == "📌 Добавить данные")
@bot.message_handler(commands=['add'])
def add(message):
    user = db.get_user(message.chat.id)
    if user:
        bot.send_message(message.chat.id, "⚠️ У тебя уже есть профиль. Используй /update, чтобы изменить его.")
        return

    msg = bot.send_message(message.chat.id, "✍️ Введи свои данные через запятую (Имя, Профессия, Опыт, Интересы):")
    bot.register_next_step_handler(msg, save_user_data)


def save_user_data(message):
    try:
        data = [x.strip() for x in message.text.split(",")]
        if len(data) != 4:
            bot.send_message(message.chat.id, "❌ Нужно ввести ровно 4 значения через запятую.")
            return

        name, profession, experience, interests = data
        db.add_user(message.chat.id, name, profession, experience, interests)
        bot.send_message(message.chat.id, "✅ Профиль успешно создан!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda m: m.text == "🎯 Выбрать профессию")
def start_career_test(message):
    db.init_career_progress(message.chat.id)
    send_career_question(message.chat.id, 1)

def send_career_question(chat_id, qid):
    qdata = db.get_career_question(qid)
    if not qdata:
        finish_career_test(chat_id)
        return
    text = f"❓ {qdata['question']}"
    markup = types.InlineKeyboardMarkup()
    for oid, opt_text in qdata["options"]:
        markup.add(types.InlineKeyboardButton(opt_text, callback_data=f"career_opt:{qid}:{oid}"))
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("career_opt:"))
def handle_career_answer(call):
    _, qid, oid = call.data.split(":")
    qid, oid = int(qid), int(oid)

    progress = db.get_progress(call.message.chat.id)
    if not progress:
        return

    with db.connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT career_ids FROM career_options WHERE id = ?", (oid,))
        row = cursor.fetchone()
        if row and row[0]:
            new_ids = [int(x) for x in row[0].split(",") if x.isdigit()]
            selected = list(set(progress["selected_careers"] + new_ids))
        else:
            selected = progress["selected_careers"]

    next_q = qid + 1
    db.update_progress(call.message.chat.id, next_q, selected)

    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_career_question(call.message.chat.id, next_q)

def finish_career_test(chat_id):
    progress = db.get_progress(chat_id)
    if not progress:
        bot.send_message(chat_id, "⚠ Ошибка: нет прогресса.")
        return

    ids = list(set(progress["selected_careers"]))
    if not ids:
        bot.send_message(chat_id, "😕 К сожалению, профессий не найдено.")
    else:
        careers = db.get_career_by_ids(ids)
        text = "🔥 Тебе могут подойти такие профессии:\n\n"
        for name, url in careers:
            text += f"💼 {name}\n🔗 {url}\n\n"
        bot.send_message(chat_id, text)

    db.clear_progress(chat_id)


@bot.message_handler(commands=['update'])
def update(message):
    user = db.get_user(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "❌ У тебя пока нет профиля. Сначала создай его через /add.")
        return

    msg = bot.send_message(message.chat.id, "🔄 Введи новые данные (Имя, Профессия, Опыт, Интересы через запятую):")
    bot.register_next_step_handler(msg, update_user_data)

def update_user_data(message):
    try:
        name, profession, experience, interests = [x.strip() for x in message.text.split(",")]
        db.update_user(message.chat.id, name, profession, experience, interests)
        bot.send_message(message.chat.id, "✅ Профиль успешно обновлён!")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка при обновлении профиля. Проверь формат.")


@bot.message_handler(func=lambda m: m.text == "👤 Мой профиль")
@bot.message_handler(commands=['profile'])
def profile(message):
    user = db.get_user(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "❌ У тебя пока нет профиля. Используй /add, чтобы создать его.")
        return

    text = (
        f"👤 Имя: {user['name']}\n"
        f"💼 Профессия: {user['profession']}\n"
        f"📚 Опыт: {user['experience']}\n"
        f"✨ Интересы: {user['interests']}"
    )
    bot.send_message(message.chat.id, text)

@bot.callback_query_handler(func=lambda call: call.data == "edit_interests")
def edit_interests(call):
    bot.send_message(call.message.chat.id, "Введите ваши интересы:")
    bot.register_next_step_handler(call.message, save_interests)

def save_interests(message):
    db.update_interests(message.chat.id, message.text)
    bot.send_message(message.chat.id, "⭐ Интересы обновлены!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "⭐ Мои интересы")
def show_interests(message):
    interests = db.get_interests(message.chat.id)
    if interests:
        bot.send_message(message.chat.id, f"⭐ Твои интересы:\n{interests}")
    else:
        bot.send_message(message.chat.id, "У тебя пока нет сохранённых интересов. Добавь их в профиле!")


@bot.message_handler(func=lambda m: m.text == "❓ Вопрос–Ответ")
def faq_section(message):
    faq_list = db.get_faq()
    text = "📖 Часто задаваемые вопросы:\n\n"
    for q, a in faq_list:
        text += f"❓ {q}\n💡 {a}\n\n"

    markup = types.InlineKeyboardMarkup()
    btn_generate = types.InlineKeyboardButton("✨ Сгенерировать советы", callback_data="generate_advices")
    btn_settings = types.InlineKeyboardButton("⚙ Настройки", callback_data="faq_settings")
    markup.add(btn_generate, btn_settings)

    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "generate_advices")
def generate_advices(call):
    user = db.get_user(call.message.chat.id)
    if user:
        _, _, name, profession, experience, interests, *_ = user
        user_data = {
            "name": name,
            "profession": profession,
            "experience": experience,
            "interests": interests
        }
    else:
        user_data = {}

    sent = bot.send_message(call.message.chat.id, "✨ Генерация персональных советов...")
    try:
        answer = gigachat.ask(
            "Сгенерируй 3 полезных карьерных совета для меня.", 
            user_data=user_data
        )
        if not answer: 
            raise ValueError("ничего нет")

        bot.delete_message(call.message.chat.id, sent.message_id)
        bot.send_message(call.message.chat.id, f"💡 {answer}")

    except Exception as e:
        import traceback
        traceback.print_exc()  
        bot.delete_message(call.message.chat.id, sent.message_id)
        bot.send_message(call.message.chat.id, "Не удалось сгенерировать советы.")









@bot.callback_query_handler(func=lambda call: call.data == "faq_settings")
def faq_settings(call):
    status = db.get_expert_mode(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    if status:
        btn = types.InlineKeyboardButton("🔴 Отключить эксперта", callback_data="toggle_expert")
    else:
        btn = types.InlineKeyboardButton("🟢 Подключить эксперта", callback_data="toggle_expert")
    markup.add(btn)
    bot.send_message(call.message.chat.id, "⚙ Настройки режима вопросов:", reply_markup=markup)







@bot.callback_query_handler(func=lambda call: call.data == "toggle_expert")
def toggle_expert(call):
    user_id = call.message.chat.id
    current = db.get_expert_mode(user_id)
    db.set_expert_mode(user_id, not current)

    if not current:
        bot.answer_callback_query(call.id, "🟢 Эксперт подключён")
        bot.send_message(user_id, "Теперь можешь задавать вопросы, и эксперт будет отвечать.")
    else:
        bot.answer_callback_query(call.id, "🔴 Эксперт отключён")
        bot.send_message(user_id, "Эксперт отключён.")


@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_user_message(message):
    user = db.get_user(message.chat.id)
    if not user:
        return

    if user.get("expert_mode"):
        db.add_message(message.chat.id, "user", message.text)

        history = db.get_history(message.chat.id, limit=20)

        sent = bot.send_message(message.chat.id, "🤔 Эксперт думает...")
        try:

            answer = gigachat.ask(history)

            db.add_message(message.chat.id, "assistant", answer)

            bot.delete_message(message.chat.id, sent.message_id)
            bot.send_message(message.chat.id, f"🧠 Эксперт: {answer}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            bot.delete_message(message.chat.id, sent.message_id)
            bot.send_message(message.chat.id, "⚠ Ошибка при обращении к эксперту.")
    else:
        return



if __name__ == "__main__":
    bot.polling(none_stop=True)
