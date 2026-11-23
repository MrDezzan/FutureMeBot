# FutureMeBot

A Telegram bot that helps teenagers and career changers choose a profession. It combines a guided questionnaire, a saved profile and an AI career consultant.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram%20Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![GigaChat](https://img.shields.io/badge/GigaChat-21A038?style=flat-square)

<img width="480" alt="FutureMeBot" src="https://github.com/user-attachments/assets/0dcdc3e3-701f-45af-9a1c-ed8a6da2cec6" />

## What it does

- **Choose a profession.** The bot asks a few questions with inline buttons and narrows down suitable directions based on the answers.
- **Profile.** Users save their name, current profession, experience and interests, and can edit them later.
- **Questions and answers.** A built-in FAQ, plus a personal AI consultant (GigaChat) that answers career questions using the saved profile and generates career advice on request.
- **Expert mode.** Users switch the consultant on or off. When it is on, any free-text message goes to the AI.
- The consultant only talks about careers and education and politely refuses other topics.

The interface is in Russian.

## Tech stack

Python, [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBot), SQLite, GigaChat API.

## Files

| File | Purpose |
|---|---|
| `main.py` | bot entry point, menus and handlers |
| `api.py` | GigaChat wrapper with the consultant's system prompt |
| `db.py` | SQLite access; tables and starter data are created on first run |
| `config.py` | your tokens and settings (see below) |

## Run it

```bash
pip install pyTelegramBotAPI gigachat
```

Fill in `config.py`:

```python
BOT_TOKEN = "token from @BotFather"
CLIENT_SECRET = "GigaChat credentials"
MODEL = "GigaChat"
```

```bash
python main.py
```

Keep `config.py` out of version control once it has real values.
