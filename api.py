from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from config import CLIENT_SECRET, MODEL

class GigaChatAPI:
    def __init__(self):
        self.client = GigaChat(
            credentials=CLIENT_SECRET,
            model=MODEL,
            verify_ssl_certs=False
        )
        self.model = MODEL

    def ask(self, history, user_data: dict = None) -> str:
        messages = []

    def ask(self, history, user_data: dict = None) -> str:
        messages = []

        messages.append(Messages(
            role=MessagesRole.SYSTEM,
            content=(
                "Ты - карьерный консультант. Отвечай дружелюбно и понятно. "
                "Используй эмодзи, но не перебарщивай. "
                "Отвечай только на вопросы связанные с карьерой и профессией. "
                "На другие темы всегда отвечай: 'Я отвечаю только на вопросы связанные с профессией (НИ КОРОТКО НИ ДЛИННО ВООБЩЕ НИКАК ПРОСТО Я ОТВЕЧАЮ ТОЛЬКО НА ВОПРОСЫ С ПРОФЕССИЕЙ)'. "
                "Не используй MarkDown в сообщениях."
            )
        ))


        if user_data:
            user_info = (
                f"Информация о пользователе:\n"
                f"Имя: {user_data.get('name')}\n"
                f"Профессия: {user_data.get('profession')}\n"
                f"Опыт: {user_data.get('experience')}\n"
                f"Интересы: {user_data.get('interests')}\n\n"
            )
            messages.append(Messages(role=MessagesRole.USER, content=user_info))


        if isinstance(history, str):
            messages.append(Messages(role=MessagesRole.USER, content=history))


        elif isinstance(history, list):
            for msg in history:
                if msg["role"] == "user":
                    role = MessagesRole.USER
                else:
                    role = MessagesRole.ASSISTANT
                messages.append(Messages(role=role, content=msg["content"]))

        else:
            raise ValueError("history должен быть строкой или списком сообщений")

        chat = Chat(messages=messages, model=self.model)
        response = self.client.chat(chat)

        print("ДЕБАГ:", response)
        return response.choices[0].message.content