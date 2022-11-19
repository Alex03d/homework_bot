import os
import sys
import time
import logging
# from http import HTTPStatus

import requests
import telegram

from telegram import Bot

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='w'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

load_dotenv()

PRACTICUM_TOKEN = 'y0_AgAAAAAJvI3SAAYckQAAAADTrQmhyh8tnQ1TQ8aZXZrLSzHFXn0NBQQ'
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = 115109068

RETRY_TIME = 6
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """
    Функция отправляет сообщение в Telegram чат.
    Чат определяется переменной окружения TELEGRAM_CHAT_ID.
    Принимает на вход два параметра:
    экземпляр класса Bot и строку с текстом сообщения.
    """
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
    """
    Функция делает запрос к единственному эндпоинту.
    В качестве параметра функция получает временную метку.
    В случае успешного запроса должна вернуть ответ API, преобразовав
    его из формата JSON к типам данных Python.
    """
    timestamp = current_timestamp or int(time.time())
    # timestamp = 0
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT,
                            headers=HEADERS,
                            params=params
                            )
    if not response:
        message = 'Ошибка соединения с сервером'
        logger.error(message)
        raise ConnectionError(message)
    if response.status_code != 200:
        message = 'API возвращает код, отличный от 200'
        logger.error(message)
        raise Exception(message)
    return response.json()


def check_response(response):
    """
    Функция проверяет ответ API на корректность.
    В качестве параметра функция получает ответ API, приведенный
    к типам данных Python. Если ответ API соответствует ожиданиям,
    то функция должна вернуть список домашних работ (он может быть
    и пустым), доступный в ответе API по ключу 'homeworks'.
    """
    if not response:
        message = 'Сервер вернул пустой массив данных'
        logger.error(message)
        raise Exception(message)
    if isinstance(response, list):
        # or isinstance(response, tuple)
        # # or isinstance(response, set)
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
    """
    Функция извлекает из информации о конкретной домашней работе статус.
    В качестве параметра функция получает только один элемент из списка
    домашних работ. В случае успеха, функция возвращает подготовленную
    для отправки в Telegram строку, содержащую один из вердиктов словаря
    HOMEWORK_STATUSES.
    """
    if 'homework_name' not in homework:
        message = 'Нет данных о домашней работе'
        logger.error(message)
        raise KeyError(message)
    if 'status' not in homework:
        message = 'Не данных о домашней работе'
        logger.error(message)
        raise KeyError(message)
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        message = 'Неизвестный статус'
        logger.error(message)
        raise Exception(message)
    verdict = HOMEWORK_STATUSES[f'{homework_status}']
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'

    # if 'homework_name' not in homework[0]:
    #     message = 'Нет данных о домашней работе'
    #     logger.error(message)
    #     raise KeyError(message)
    # if 'status' not in homework[0]:
    #     message = 'Не данных о домашней работе'
    #     logger.error(message)
    #     raise KeyError(message)
    # homework_name = homework[0]['homework_name']
    # homework_status = homework[0]['status']
    # if homework_status not in HOMEWORK_STATUSES:
    #     message = 'Неизвестный статус'
    #     logger.error(message)
    #     raise Exception(message)
    # verdict = HOMEWORK_STATUSES[homework_status]
    # return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """
    Функция проверяет доступность переменных окружения.
    Если отсутствует хотя бы одна переменная окружения —
    функция должна вернуть False, иначе — True.
    """
    list_of_tokens = (TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID)
    for token in list_of_tokens:
        if str(token) is None:
            message = f'Отсутствие {token}'
            logger.critical(message)
            raise TypeError(message)
            return False
        return True


def main():
    """
    Описана основная логика работы программы.
    Все остальные функции должны запускаться из неё.
    """
    if check_tokens() is True:
        pass
    else:
        raise ValueError(
            'отсутствие обязательных переменных окружения '
            'во время запуска бота ')
        sys.exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    # current_timestamp = 0

    while True:
        try:
            response = get_api_answer(current_timestamp)
            if not response['homeworks']:
                current_timestamp = response['current_date']
                logger.info('Сработал time.sleep при пустом списке')
                time.sleep(RETRY_TIME)
            else:
                homework = check_response(response)
                message = parse_status(homework)
                send_message(bot, message)
                logger.info('Сообщение успешно отправлено')
                time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            logger.info('Программа работает без сбоев')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
