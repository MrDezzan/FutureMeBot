import telebot
from config import BOT_TOKEN
from database import DBManager

bot = telebot.TeleBot(BOT_TOKEN)
db = DBManager()

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "👋 Привет! Это FutureMe - бот помощник в выборе профессии.\n\n"
        "Если ты только начинаешь карьеру – отправь свои данные командой /add.\n"
        "Если ты уже работаешь, но хочешь найти новую работу – тоже используй /add.\n\n"
        "📌 После этого я помогу тебе сохранить информацию."
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['add'])
def add(message):
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    name = message.text
    bot.send_message(message.chat.id, "Введите вашу профессию:")
    bot.register_next_step_handler(message, get_profession, name)

def get_profession(message, name):
    profession = message.text
    bot.send_message(message.chat.id, "Опишите ваш опыт:")
    bot.register_next_step_handler(message, save_user, name, profession)

def save_user(message, name, profession):
    experience = message.text
    db.add_user(message.chat.id, name, profession, experience)
    bot.send_message(message.chat.id, "✅ Данные сохранены!")

if __name__ == "__main__":
    bot.polling(none_stop=True)
