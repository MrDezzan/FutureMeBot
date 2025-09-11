import sqlite3

class DBManager:
    def __init__(self, db_path: str = "futureme.db"):
        self.db_path = db_path
        self.create_tables()
        self.default_insert()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    telegram_id INTEGER UNIQUE,
                    name TEXT,
                    profession TEXT,
                    experience TEXT,
                    interests TEXT,
                    expert_mode INTEGER DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS faq (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT,
                    answer TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    role TEXT,         -- "user" или "assistant"
                    content TEXT
                )
            """)

            conn.commit()

    def default_insert(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM faq")
            if cursor.fetchone()[0] == 0:
                faq_data = [
                    ("Нужно ли платить за использование бота?", "Нет, бот бесплатный."),
                    ("Можно ли сохранять профессии?", "Да, через меню ⭐ Мои интересы."),
                    ("Что если я не нашёл подходящую профессию?", "Попробуй описать себя по-другому. Например: не «хочу айти», а «люблю разбираться в компьютерах и программировать»."),
                    ("Для кого этот бот?", "Для подростков, взрослых и всех, кто ищет новые пути развития.")
                ]
                cursor.executemany("INSERT INTO faq (question, answer) VALUES (?, ?)", faq_data)

            cursor.execute("SELECT COUNT(*) FROM ai_questions")
            if cursor.fetchone()[0] == 0:
                ai_qs = [
                    ("Какие предметы тебе нравились в школе больше всего?"),
                    ("Ты больше любишь работать с людьми или с компьютером?"),
                    ("Что тебе ближе — творческая работа или строгие правила и порядок?"),
                    ("Ты хочешь работать в офисе или на удалёнке?"),
                    ("Что для тебя важнее — высокая зарплата или интересная работа?"),
                    ("Представь, что у тебя много свободного времени: чем бы ты занимался?")
                ]
                cursor.executemany("INSERT INTO ai_questions (question) VALUES (?)", [(q,) for q in ai_qs])

            conn.commit()

    def add_user(self, telegram_id: int, name: str, profession: str, experience: str, interests: str):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT OR REPLACE INTO users (chat_id, telegram_id, name, profession, experience, interests)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (telegram_id, telegram_id, name, profession, experience, interests))
            conn.commit()
    def add_message(self, user_id: int, role: str, content: str):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
            conn.commit()

    def get_history(self, user_id: int, limit: int = 20):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, content FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
            rows = cursor.fetchall()
            return [{"role": r, "content": c} for r, c in rows[::-1]]

    def clear_history(self, user_id: int):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
            conn.commit()



    def get_user(self, chat_id):
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
            row = cur.fetchone()
            if row:
                columns = [col[0] for col in cur.description]
                return dict(zip(columns, row))
            return None

    def set_expert_mode(self, telegram_id: int, status: bool):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET expert_mode = ? WHERE telegram_id = ?", (1 if status else 0, telegram_id))
            conn.commit()

    def get_expert_mode(self, telegram_id: int) -> bool:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT expert_mode FROM users WHERE telegram_id = ?", (telegram_id,))
            result = cursor.fetchone()
            return bool(result[0]) if result else False


    def update_interests(self, telegram_id: int, interests: str):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET interests = ? WHERE telegram_id = ?", (interests, telegram_id))
            conn.commit()

    def get_interests(self, telegram_id: int) -> str:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT interests FROM users WHERE telegram_id = ?", (telegram_id,))
            result = cursor.fetchone()
            return result[0] if result else ""
    def set_expert_mode(self, telegram_id: int, status: bool):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET expert_mode = ? WHERE telegram_id = ?", (1 if status else 0, telegram_id))
            conn.commit()

    def get_expert_mode(self, telegram_id: int) -> bool:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT expert_mode FROM users WHERE telegram_id = ?", (telegram_id,))
            result = cursor.fetchone()
            return bool(result[0]) if result else False

    def get_faq(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT question, answer FROM faq")
            return cursor.fetchall()

    def get_ai_questions(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT question FROM ai_questions")
            return [row[0] for row in cursor.fetchall()]
