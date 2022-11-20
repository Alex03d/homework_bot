import json
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from telegram import Bot
from endpoint import ENDPOINT


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = 115109068

TELEGRAM_RETRY_TIME = 600
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка любых сообщений в ТГ чат: обновления домашки, ошибки."""
    bot = Bot(token=TELEGRAM_TOKEN)
    chat_id = TELEGRAM_CHAT_ID
    try:
        bot.send_message(chat_id, message)
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения в Telegram. '
                     f'Ошибка - {error}')
    else:
        logger.info('Удачная отправка сообщения в Telegram.')


def get_api_answer(current_timestamp):
    """Запрос к единственному эндпоинту и проверка доступности сервера."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT,
                            headers=HEADERS,
                            params=params
                            )
    if response.status_code == HTTPStatus.OK:
        try:
            response.json()
        except json.decoder.JSONDecodeError:
            message = 'Ответ API не преобразовалcя в JSON'
            logger.error(message)
    elif response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        message = 'Ошибка 500 сервера'
        logger.error(message)
        raise ConnectionError(message)
    else:
        message = 'Не удалось соединиться с сервером'
        logger.error(message)
        raise ConnectionError(message)


def check_response(response):
    """Проверка ответа API на корректность."""
    message = 'Начало проверки ответа сервера'
    logger.debug(message)
    if not response:
        message = 'Сервер вернул пустой массив данных'
        logger.error(message)
        raise Exception(message)
    if isinstance(response, tuple):
        message = 'отсутствие ожидаемых ключей в ответе API: dict'
        logger.error(message)
        raise Exception(message)
    if not isinstance(response['homeworks'], list):
        message = ('отсутствие ожидаемых ключей в ответе API: '
                   'ожидается список домашних работ')
        logger.error(message)
        raise Exception(message)
    return response.get('homeworks')[0]


def parse_status(homework):
    """Извлечение статуса домашки."""
    if 'homework_name' not in homework:
        message = 'Нет данных о домашней работе'
        logger.error(message)
        raise KeyError(message)
    if 'status' not in homework:
        message = 'Не данных о домашней работе'
        logger.error(message)
        raise KeyError(message)
    if not homework['homework_name'] or homework['homework_name'] is None:
        message = 'Не данных о названии домашней работы'
        logger.error(message)
        raise KeyError(message)
    if not homework['status'] or homework['status'] is None:
        message = 'Не данных о статусе домашней работы'
        logger.error(message)
        raise KeyError(message)
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        message = 'Неизвестный статус'
        logger.error(message)
        raise Exception(message)
    verdict = HOMEWORK_VERDICTS[f'{homework_status}']
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности токенов."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """
    Описана основная логика работы программы.
    Все остальные функции должны запускаться отсюда.
    """
    if not check_tokens():
        logger.error('Отсутствие переменных окружений')
        return sys.exit('Неполадки с переменными окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            if not response['homeworks']:
                current_timestamp = response['current_date']
                logger.info('Сработал time.sleep при пустом списке')
                time.sleep(TELEGRAM_RETRY_TIME)
            else:
                homework = check_response(response)
                message = parse_status(homework)
                send_message(bot, message)
                logger.info('Сообщение успешно отправлено')
                time.sleep(TELEGRAM_RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(TELEGRAM_RETRY_TIME)
        else:
            logger.info('Программа работает без сбоев')
        finally:
            time.sleep(TELEGRAM_RETRY_TIME)


if __name__ == '__main__':
    main()
