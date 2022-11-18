WARNING: Running pip as root will break packages and permissions. You should install packages reliably by using venv: https://pip.pypa.io/warnings/venv
----------------------- Проверка flake8 пройдена -----------------------

============================= test session starts ==============================
platform linux -- Python 3.7.4, pytest-6.2.5, py-1.10.0, pluggy-0.13.1 -- /usr/local/bin/python
rootdir: /app, configfile: pytest.ini, testpaths: tests/
plugins: django-3.8.0
collecting ... collected 17 items

tests/test_bot.py::TestHomework::test_check_tokens_false FAILED          [  5%]
tests/test_bot.py::TestHomework::test_check_tokens_true PASSED           [ 11%]
tests/test_bot.py::TestHomework::test_bot_init_not_global PASSED         [ 17%]
tests/test_bot.py::TestHomework::test_logger PASSED                      [ 23%]
tests/test_bot.py::TestHomework::test_send_message PASSED                [ 29%]
tests/test_bot.py::TestHomework::test_get_api_answers PASSED             [ 35%]
tests/test_bot.py::TestHomework::test_get_500_api_answer PASSED          [ 41%]
tests/test_bot.py::TestHomework::test_parse_status FAILED                [ 47%]
tests/test_bot.py::TestHomework::test_check_response PASSED              [ 52%]
tests/test_bot.py::TestHomework::test_parse_status_unknown_status PASSED [ 58%]
tests/test_bot.py::TestHomework::test_parse_status_no_status_key PASSED  [ 64%]
tests/test_bot.py::TestHomework::test_parse_status_no_homework_name_key PASSED [ 70%]
tests/test_bot.py::TestHomework::test_check_response_no_homeworks PASSED [ 76%]
tests/test_bot.py::TestHomework::test_check_response_not_dict FAILED     [ 82%]
tests/test_bot.py::TestHomework::test_check_response_homeworks_not_in_list PASSED [ 88%]
tests/test_bot.py::TestHomework::test_check_response_empty FAILED        [ 94%]
tests/test_bot.py::TestHomework::test_api_response_timeout FAILED        [100%]

=================================== FAILURES ===================================
/app/homework.py:142: TypeError: Отсутствие PRACTICUM_TOKEN
/app/homework.py:115: KeyError: 0
/app/homework.py:98: Exception: отсутствие ожидаемых ключей в ответе API: dict
/app/homework.py:79: ConnectionError: Ошибка соединения с сервером
/app/tests/test_bot.py:639: AssertionError: Убедитесь, что в функции `check_response` обрабатываете ситуацию, когда API возвращает код, отличный от 200
=========================== short test summary info ============================
FAILED tests/test_bot.py::TestHomework::test_check_tokens_false - TypeError: ...
FAILED tests/test_bot.py::TestHomework::test_parse_status - KeyError: 0
FAILED tests/test_bot.py::TestHomework::test_check_response_not_dict - Except...
FAILED tests/test_bot.py::TestHomework::test_check_response_empty - Connectio...
FAILED tests/test_bot.py::TestHomework::test_api_response_timeout - Assertion...
========================= 5 failed, 12 passed in 0.17s