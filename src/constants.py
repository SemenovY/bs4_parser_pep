"""
Сейчас в коде есть вот такие константы.

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
Вынесем её в константу MAIN_DOC_URL.
"""
from pathlib import Path


BASE_DIR = Path(__file__).parent
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

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


# ヽ(´▽`)/

# kaonashi
# =^..^=______/
