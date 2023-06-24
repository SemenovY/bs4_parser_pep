"""
Первым делом соберём все константы в одном месте.

Сейчас в коде есть вот такие константы:
BASE_DIR в файле download.py. В ней хранится абсолютный путь до директории
проекта.
WHATS_NEW_URL в файле whats_new.py со ссылкой
https://docs.python.org/3/whatsnew/.
MAIN_DOC_URL в файле latest_version.py со ссылкой
https://docs.python.org/3/.
DOWNLOADS_URL в файле download.py со ссылкой
https://docs.python.org/3/download.html.
У констант WHATS_NEW_URL, MAIN_DOC_URL, DOWNLOADS_URL есть общая
часть —  https://docs.python.org/3/.
Вынесем её в константу MAIN_DOC_URL,
а если нужная ссылка для парсера не будет совпадать со значением константы,
заведём для неё переменную, в которой сформируем полную ссылку
при помощи функции urljoin().
"""
from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
# Адрес страницы pep
PEP_URL = 'https://peps.python.org/'
# Константа, где будет храниться путь до директории с текущим файлом.
BASE_DIR = Path(__file__).parent
# Формат для записи даты и времени
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
# Указываем формат времени.
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
# Описание формата логов:
# Время записи – Уровень сообщения – Cообщение.
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

# Статусы
EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}
# LOG_DIR = BASE_DIR / 'logs'
# RESULTS_DIR = BASE_DIR / 'results'


# ヽ(´▽`)/

# kaonashi
# =^..^=______/
