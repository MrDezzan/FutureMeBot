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

        messages.append(Messages(
            role=MessagesRole.SYSTEM,
            content=(
                "Ты — карьерный консультант. Отвечай только на вопросы, связанные с профессией, карьерой, образованием, навыками и поиском работы. "
                "Если вопрос не связан с этими темами — НИКОГДА НЕ ОТВЕЧАЙ и возвращай строго один ответ без вариаций: "
                "'Я отвечаю только на вопросы связанные с профессией.' Но не добавляй это на все вопросы только на эти "
                "Не добавляй ничего лишнего, никаких пояснений, никаких смайлов кроме одного в начале, никаких обходов. "
                "Запрещено объяснять, почему ты не отвечаешь. Разрешён только один ответ в таких случаях."
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
            messages.append(Messages(
                role=MessagesRole.USER,
                content=user_info
            ))

        for msg in history:
            if msg["role"] == "user":
                role = MessagesRole.USER
            else:
                role = MessagesRole.ASSISTANT

            messages.append(Messages(
                role=role,
                content=msg["content"]
            ))

        chat = Chat(messages=messages, model=self.model)
        response = self.client.chat(chat)

        print("ДЕБАГ:", response)
        return response.choices[0].message.content
