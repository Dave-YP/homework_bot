import os
import logging
import time

import telegram
import requests
from dotenv import load_dotenv
from http import HTTPStatus
import sys

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] - %(message)s'
    )
handler.setFormatter(formatter)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ])


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logging.debug('Сообщение отправлено.')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(f'Бот отправил сообщение: {message}')
    except Exception as error:
        logger.error(f'Ошибка отправки сообщения: {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        )
    except Exception:
        raise ConnectionError('Нет подключения к серверу')
    if response.status_code != HTTPStatus.OK:
        raise Exception(
            f'{ENDPOINT} недоступен.'
            f'Код ответа API: {response.status_code}')
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logger.info('Начинаем проверку ответа сервера')
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарем.')
    if not all(['current_date' in response, 'homeworks' in response]):
        raise KeyError('В ответе API нет ключей')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Homeworks не список')
    return response['homeworks']


def parse_status(homework):
    """Извлекает статус домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('В ответе не найден ключ homework_name')
    homework_name = homework["homework_name"]
    if 'status' not in homework:
        raise KeyError('В ответе отсутствует status')
    status = homework["status"]
    if status not in HOMEWORK_VERDICTS:
        raise KeyError('Недокументированный статус домашней работы')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    previous_status = ''
    if not check_tokens():
        logger.critical('Отсутствуют переменные окружения.Остановка программы')
        sys.exit()
    while True:
        try:
            logger.debug('Запрос к API')
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                if message != previous_status:
                    send_message(bot, message)
                    previous_status = message
            else:
                logger.debug('Нет нового статуса')
            current_timestamp = response.get('current_date')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != previous_status:
                send_message(bot, message)
                previous_status = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
