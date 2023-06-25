"""
Парсер будет выполнять три функции.

Собирать ссылки на статьи о нововведениях в Python,
переходить по ним и забирать информацию об авторах и редакторах статей.
Собирать информацию о статусах версий Python.
Скачивать архив с актуальной документацией.

Первый парсер: будет переходить по ссылкам.
Второй парсер: будет собирать информацию о версиях Python — номера,
статусы (in development, pre-release, stable и так далее)
и ссылки на документацию.
Третий парсер: будет скачивать архив с документацией Python на локальный диск.

# Запуск парсера информации из статей о нововведениях в Python.
(venv) ...$ python main.py whats-new

# Запуск парсера статусов версий Python.
(venv) ...$ python main.py latest-versions

# Запуск парсера, который скачивает архив документации Python.
(venv) ...$ python main.py download
"""
import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, get_response


# Собираем ссылки, забираем информацию об авторах и редакторах статей.
def whats_new(session):
    """Первый парсер: будет переходить по ссылкам."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python, desc='Выполнение цикла парсинга'):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        response = get_response(session, version_link)
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
        return results


# Информация о версиях Python — номера, статусы и ссылки на документацию.
def latest_versions(session):
    """
    Второй парсер будет собирать информацию о версиях Python.

    Номера, статусы (in development, pre-release, stable и так далее)
    и ссылки на документацию.
    """
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        raise AssertionError('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


# Скачиваем архив документации Python.
def download(session):
    """Парсер будет скачивать архив с документацией Python на диск."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


# Со страницы pep получаем данные о статусе и выводим в таблицу.
def pep(session):
    """
    На главной странице находим ссылки на pep.

    На странице pep считываем статус и заносим в словарь
    Словарь из модуля collection, используем для значения по умолчанию
    для новых значений, defaultdict(int) через get
    Делаем проверку на несовпадающий статус и вывод лога в консоль.
    Через цикл заполняем таблицу.
    """
    # Шаг 1 - Закрепимся на главной странице, найдем точку входа в pep_index
    response = get_response(session, PEP_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')

    # Шаг 2 - Получаем ссылки, варим новый суп и пробегаемся по всем pep_pages.
    result = [('Cтатус', 'Количество')]
    count_pep_status = defaultdict(int)
    for index in tqdm(range(1, len(tr_tags)), desc='Выполнение цикла'):
        pep_href_tag = tr_tags[index].a['href']
        pep_link = urljoin(PEP_URL, pep_href_tag)
        response = get_response(session, pep_link)
        soup = BeautifulSoup(response.text, features='lxml')
        main_card_tag = find_tag(soup, 'section', {'id': 'pep-content'})
        main_card_dl_tag = find_tag(
            main_card_tag, 'dl',
            {'class': 'rfc2822 field-list simple'}
            )

        # Шаг 3 - На странице pep находим статус, добавляем в dict
        for tag in main_card_dl_tag:
            if tag.name == 'dt' and tag.text == 'Status:':
                card_status = tag.next_sibling.next_sibling.string
                count_pep_status[card_status] = count_pep_status.get(
                    card_status, 0) + 1

                # Шаг 4 - Проверка на наличие статуса в main_page и совпадение
                if len(tr_tags[index].td.text) != 1:
                    table_status = tr_tags[index].td.text[1:]
                    if card_status[0] != table_status:
                        logging.info(
                            '\n'
                            'Несовпадающие статусы:\n'
                            f'{pep_link}\n'
                            f'Статус в карточке: {card_status}\n'
                            f'Ожидаемые статусы: '
                            f'{EXPECTED_STATUS[table_status]}\n'
                        )

    # Шаг 5 - Загоняем данные из словаря в таблицу и добавим Total.
    for key in count_pep_status:
        result.append((key, str(count_pep_status[key])))
    result.append(('Total', len(tr_tags) - 1))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


# Запуск логирования, выбор режима работы
def main():
    """
    Запускаем программу, логирование.

    Выбираем из arg режим работы
    При необходимости чистим кеш
    """
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()


# ヽ(´▽`)/

# kaonashi
# =^..^=______/
