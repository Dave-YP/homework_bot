# homework-bot
Чат-бот Telegram для получения информации о статусе домашней работы.

Как запустить программу:
1.	Клонируйте репозитроий с программой:
git clone https://github.com/Dave-YP/homework_bot.git

2.	В созданной директории установите виртуальное окружение, активируйте его и установите необходимые зависимости:
```sh
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

1.	Создайте чат-бота Telegram.
2.	Создайте в директории файл .env и поместите туда необходимые токены в формате PRAKTIKUM_TOKEN = 'ххххххххх', TELEGRAM_TOKEN = 'ххххххххххх', TELEGRAM_CHAT_ID = 'ххххххххххх'
3.	Запустите homework.py командой:
```sh
python homework.py runserver.
```
