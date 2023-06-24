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

Так же
Библиотека PrettyTable
PrettyTable — это дополнительный модуль Python, который позволяет создавать
простые таблицы и выводить их в терминал, текстовый файл или передавать
на обработку в другие программы.
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


def whats_new(session):
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
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
        return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
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


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
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


def pep(session):
    response = get_response(session, PEP_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')
    result = [('Cтатус', 'Количество')]
    pep_sum = defaultdict(int)

    for index in range(1, len(tr_tags)):
        pep_href_tag = tr_tags[index].a['href']
        pep_link = urljoin(PEP_URL, pep_href_tag)
        response = get_response(session, pep_link)
        soup = BeautifulSoup(response.text, 'lxml')
        main_card_tag = find_tag(soup, 'section', {'id': 'pep-content'})
        main_card_dl_tag = find_tag(
            main_card_tag, 'dl',
            {'class': 'rfc2822 field-list simple'}
            )

        for tag in tqdm(main_card_dl_tag):
            if tag.name == 'dt' and tag.text == 'Status:':
                card_status = tag.next_sibling.next_sibling.string
                pep_sum[card_status] = pep_sum.get(card_status, 0) + 1

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

    for key in pep_sum:
        result.append((key, str(pep_sum[key])))
    result.append(('Total', len(tr_tags) - 1))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
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
