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

    def ask(self, prompt: str, user_data: dict = None) -> str:
        context = ""
        if user_data:
            context = (
                f"Информация о пользователе:\n"
                f"Имя: {user_data.get('name')}\n"
                f"Профессия: {user_data.get('profession')}\n"
                f"Опыт: {user_data.get('experience')}\n"
                f"Интересы: {user_data.get('interests')}\n\n"
            )

        chat = Chat(
            messages=[
                Messages(
                    role=MessagesRole.SYSTEM,
                    content=(
                        "Ты — карьерный консультант. Отвечай дружелюбно и понятно. "
                        "Используй эмодзи, но не перебарщивай. "
                        "Отвечай только на вопросы связанные с карьерой и профессией. "
                        "На другие темы всегда отвечай: 'Я отвечаю только на вопросы связанные с профессией (НИ КОРОТКО НИ ДЛИННО ВООБЩЕ НИКАК ПРОСТО Я ОТВЕЧАЮ ТОЛЬКО Н АВОПРОСЫ С ПРОФЕССИЕЙ)'."
                    )
                ),
                Messages(
                    role=MessagesRole.USER,
                    content=context + prompt
                )
            ],
            model=self.model
        )
        response = self.client.chat(chat)
        print("ДЕБАГ:", response)
        return response.choices[0].message.content

