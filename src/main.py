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
# Импортируйте модуль для работы с логами.
import logging
# Импортируйте модуль для работы с регулярными выражениями.
import re
# Импортируем функцию объединения ссылок из библиотеки.
from urllib.parse import urljoin

# Импорт функции для работы с кешем
import requests_cache
# Импорт нового класса из библиотеки.
from bs4 import BeautifulSoup
# Импорт функции tqdm из модуля tqdm для вывода прогресс-бара.
from tqdm import tqdm

# Импорт функции с конфигурацией парсера аргументов командной строки.
from configs import configure_argument_parser, configure_logging
# Импортируем константы
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
# Контролировать вывод результатов в программе будет эта функция
from outputs import control_output
# Обработка ошибок
from utils import find_tag, get_response


def whats_new(session):
    """
    Получение ссылок.

    Получить доступ к атрибуту тега в библиотеке bs4 можно,
    используя такой же синтаксис, как при обращении
    к ключам словаря — version_a_tag['href'].
    В теге href содержится неполная,
    относительная ссылка — href="3.9.html"
    По относительной ссылке парсер не сможет перейти на страницу,
    поэтому нужно получить полную — объединить относительную ссылку
    с адресом страницы, на которой она находится. Этот адрес хранится
    в константе WHATS_NEW_URL — https://docs.python.org/3/whatsnew/.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    # Получаем страницу и исправляем ошибки авто кодировки + логи
    response = get_response(session, whats_new_url)
    if response is None:
        # Если основная страница не загрузится, программа закончит работу.
        return

    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')

    # Шаг 1-й: поиск в "супе" тега section с нужным id.
    # Парсеру нужен только
    # первый элемент, поэтому используется метод find() через функцию find_tag.
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})

    # Шаг 2-й: поиск внутри main_div следующего тега div
    # с классом toctree-wrapper.
    # Здесь тоже нужен только первый элемент, используется метод find()
    # через функцию find_tag.
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    # Шаг 3-й: поиск внутри div_with_ul всех элементов списка
    # li с классом toctree-l1.
    # Нужны все теги, поэтому используется метод find_all().
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    # Парсер нашёл все элементы, которые хранятся в теге <li>
    # с классом toctree-l1, и сохранил их в переменную sections_by_python.
    # Там лежат и нужные ссылки — в тегах <a>.

    # Инициализируем список results.
    # Добавьте в пустой список заголовки таблицы.
    # Для PrettyTable нужно задать заголовки. Для этого замените пустую
    # инициализацию списка results на инициализацию с заголовками таблицы.
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    # прогресс-бар из библиотеки tqdm
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        # Получаем относительный адрес из атрибута href и
        # сгенерируем абсолютную ссылку с помощью функции urljoin():
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        # функция urljoin из стандартной библиотеки urllib.
        # Она корректно обрабатывает ссылки, записанные по-разному.

        # Загружаем все страницы со статьями. Используем кеширующую сессию.
        # Укажем кодировку utf-8.
        response = get_response(session, version_link)
        if response is None:
            # Если страница не загрузится, программа перейдёт к
            # следующей ссылке.
            continue

        # Сварим "супчик".
        soup = BeautifulSoup(response.text, 'lxml')
        # Найдем в "супе" тег h1.
        h1 = find_tag(soup, 'h1')
        # Найдем в "супе" тег dl.
        dl = find_tag(soup, 'dl')
        # Добавьте в вывод на печать текст из тегов h1 и dl.
        # Чтобы вывод в терминале выглядел аккуратно,
        # нужно заменить пустые строчки на пробелы.
        # Пустые строчки содержатся в теге <dl>.
        # Создадим новую переменную для вывода на печать информации
        # из тега <dl> — dl_text.
        # Через метод replace заменим пустые строки \n на пробелы ' '.
        dl_text = dl.text.replace('\n', ' ')
        # На печать теперь выводится переменная dl_text — без пустых строчек.
        # print(version_link, h1.text, dl_text)
        # Добавьте в список ссылки и текст из тегов h1 и dl в виде кортежа.
        results.append(
            (version_link, h1.text, dl_text)
        )
        # Вместо вывода списка на печать верните этот список.
        return results


def latest_versions(session):
    """
    Второй парсер: будет собирать информацию о версиях Python.

     — номера, статусы (in development, pre-release, stable и так далее)
    и ссылки на документацию.
    """
    # Получаем страницу
    # Исправляем ошибки авто кодировки + логи
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')
    # Теперь допишите команды поиска всех тегов <ul> в левой части страницы:
    # Найдите тег <div> c классом sphinxsidebarwrapper.
    # Запишите его в переменную sidebar.
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    # Внутри sidebar найдите все теги <ul>, запишите их в ul_tags.
    ul_tags = sidebar.find_all('ul')
    # В переменной ul_tags хранятся два списка с тегами <ul>,
    # но вашему парсеру нужен только первый. Его можно найти по тексту,
    # который содержится в строках списка, например, по фразе All versions —
    # это делается через цикл.
    # Циклу задаётся условие: если в списке есть фраза All versions,
    # то нужно найти в нём все теги <a>, а если нет — вывести сообщение
    # «Ничего не нашлось».
    # Перебор в цикле всех найденных списков.
    for ul in ul_tags:
        # Проверка, есть ли искомый текст в содержимом тега.
        if 'All versions' in ul.text:
            # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all('a')
            # Остановка перебора списков.
            break
    # Если нужный список не нашёлся,
    # вызывается исключение и выполнение программы прерывается.
    else:
        # not for 3.11 raise Exception
        raise AssertionError('Ничего не нашлось')

    # Вы получили нужный список, можно доставать из него
    # номера версий Python и их статусы.
    # Это значит, что пора переходить к работе с регулярными выражениями.
    # Для работы с регулярными выражениями в Python используется модуль
    # стандартной библиотеки re.
    # Один из самых популярных методов модуля — re.search().
    # У него два обязательных параметра:
    # string — строка, в которой осуществляется поиск;
    # pattern — шаблон, написанный на языке регулярных выражений,
    # который определяет правила поиска.
    # У r-строк другое назначение — они отключают экранирование символов,
    # за которое отвечает символ обратного слеша \, то есть служебные
    # последовательности в такой строке, например, \n или \t,
    # становятся обычными символами.
    # С регулярками удобно работать через r-строки, потому что в них часто
    # используются обратные слеши — либо в последовательностях,
    # либо для экранирования
    # План такой:
    # Импортируйте модуль re.
    # Извлеките ссылку из тега <a>, сохраните её в переменную link.
    # При помощи регулярного выражения pattern извлеките
    # из тега <a> номер версии и статус Python.
    # Номер версии сохраните в переменную version,
    # а статус — в status. Если строка не соответствует
    # регулярному выражению, то сохраните её полностью в переменную version,
    # а переменной status присвойте пустую строку.
    # Добавьте переменные link, version, status в список results
    # в виде кортежа.
    # Список для хранения результатов.
    # Добавьте в пустой список заголовки таблицы.
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    # Шаблон для поиска версии и статуса:
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    # Цикл для перебора тегов <a>, полученных ранее.
    for a_tag in a_tags:
        # Извлечение ссылки.
        link = a_tag['href']
        # Поиск паттерна в ссылке.
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            # Из найденного объекта парсеру нужен только текст.
            # Его можно извлечь с помощью метода group().
            # По умолчанию метод возвращает всю найденную строку.
            # Чтобы вернуть конкретную группу символов, нужно в скобках
            # указать её индекс или имя. 0 — это вся строка,
            # 1 — первая группа в регулярном выражении, и дальше по порядку.
            # Если строка соответствует паттерну,
            # переменным присываивается содержимое групп, начиная с первой.
            version, status = text_match.groups()
        else:
            # Если строка не соответствует паттерну,
            # первой переменной присваивается весь текст,
            # второй — пустая строка.
            version, status = a_tag.text, ''
        # Добавление полученных переменных в список в виде кортежа.
        results.append((link, version, status))
    # Вместо вывода списка на печать верните этот список.
    return results


def download(session):
    """
    Парсер будет скачивать архив с документацией Python.

    На локальный диск.
    """
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    # Получаем страницу
    # Исправляем ошибки авто кодировки + логи
    response = get_response(session, downloads_url)
    if response is None:
        return

    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')
    # На веб-странице нужные парсеру файлы находятся в табличке
    # Нужно достать эту таблицу из «супа».
    # Один из вариантов поиска пути до нужных тегов выглядит так:
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    # Добавьте команду получения нужного тега.
    # У нужного тега <a> нет ни id, ни класса — никаких атрибутов, кроме
    # href со значением archives/python-3.9.7-docs-pdf-a4.zip. Значение —
    # это относительная ссылка, по которой скачивается нужный архив.
    # В тексте ссылки содержится номер версии Python. Если номер изменится,
    # ссылка станет другой. Чтобы в такой ситуации парсер продолжал работать,
    # нужно искать тег по неизменной части атрибута href, например,
    # по pdf-a4.zip. Это можно сделать через регулярные выражения, которые,
    # так же как строки и списки, могут быть значениями для поиска
    # в методах find() и find_all().
    # Строка, которая заканчивается на pdf-a4.zip, соответствует регулярному
    # выражению r'.+pdf-a4\.zip$':
    # .+ — текст до значения pdf-a4.zip. Точка — любой символ кроме перевода
    # строки, а знак «плюс» означает, что слева от pdf-a4.zip может быть любое
    # количество разных символов — от одного до бесконечности.
    # pdf-a4\.zip — искомый текст. \. — это обычная точка, а не любой символ,
    # как в первом пункте, так как перед точкой стоит символ
    # экранирования — обратный слеш.
    # $ — конец строки. Без него подойдут строки, которые заканчиваются
    # на pdf-a4.zippo, pdf-a4.zip12345, pdf-a4.zipzipzip и любые другие.
    # Чтобы использовать регулярное выражение в find(), нужно указать методу
    # правильное направление для поиска: «найди строку, которая соответствует
    # регулярному выражению». Для этого в параметры метода передаётся объект
    # регулярного выражения. Он создаётся при помощи
    # функции compile() модуля re. Функция принимает строку, а возвращает
    # объект регулярного выражения.
    pdf_a4_tag = find_tag(table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    # Но ссылка неполная, относительная. Чтобы получить абсолютную ссылку,
    # нужно использовать функцию urljoin из модуля urllib.
    # Сохраните в переменную содержимое атрибута href.
    pdf_a4_link = pdf_a4_tag['href']
    # Получите полную ссылку с помощью функции urljoin.
    archive_url = urljoin(downloads_url, pdf_a4_link)
    # Для того чтобы сохранить файл на диск, нужно указать программе,
    # с каким именем и куда его сохранять.
    # Придумывать новое имя файлу необязательно. Можно использовать то,
    # которое указано на сайте.
    # Для ссылки
    # https://docs.python.org/3/archives/python-3.9.7-docs-pdf-a4.zip
    # это делается так: текст ссылки разбивается на список по слешам при
    # помощи метода split('/') и берётся последний элемент [-1].
    filename = archive_url.split('/')[-1]
    # Теперь ваша программа знает, с каким именем сохранять файл на диск.
    # Следующий шаг — указать ей место, куда этот файл сохранять.
    # Чтобы в рабочем каталоге был порядок, создайте для загружаемых файлов
    # отдельную директорию downloads. Это можно сделать при помощи
    # метода Path.mkdir() из модуля pathlib стандартной библиотеки Python.
    # Первым делом помогите программе узнать, где на диске хранится сам проект.
    # Это делается при помощи конструкции BASE_DIR = Path(__file__).parent,
    # которая возвращает путь до директории с текущим файлом, где:
    # Path(__file__) — абсолютный путь до текущего файла;
    # parent — директория, в которой он лежит.
    # Затем сформулируйте путь до новой директории; к пути до директории
    # с проектом через слеш добавьте путь до новой директории:
    # downloads_dir = BASE_DIR / 'downloads'.
    # И, наконец, создайте директорию. Для этого в модуле pathlib
    # используйте метод Path.mkdir(). Добавьте к методу параметр exist_ok=True,
    # чтобы при повторном создании такой же директории не возникала
    # ошибка FileExistsError.
    # Сформируйте путь до директории downloads.
    downloads_dir = BASE_DIR / 'downloads'
    # Создайте директорию.
    downloads_dir.mkdir(exist_ok=True)
    # Получите путь до архива, объединив имя файла с директорией.
    archive_path = downloads_dir / filename
    # Скачивание архива с документацией Python
    # Пришло время довести дело до конца — скачать архив с документацией.
    # Сначала через метод get() нужно получить HTTP-ответ от сервера на
    # загрузку архива по ссылке, которая уже есть у парсера, — она хранится
    # в переменной archive_url.
    # Следующий шаг — с помощью контекстного менеджера with записать в файл
    # полученный HTTP-ответ. Для этого открывается на запись файл, который
    # будет храниться на диске в месте, заданном переменной archive_path.
    # Так как записать нужно не обычный текст, а содержимое
    # архива — указывается бинарный режим — wb (англ. write binary).
    # Заключительный шаг — запись HTTP-ответа с помощью атрибута content.
    # Здесь весь уже написанный код.

    # Загрузка архива по ссылке.
    response = session.get(archive_url)
    # В бинарном режиме открывается файл на запись по указанному пути.
    with open(archive_path, 'wb') as file:
        # Полученный ответ записывается в файл.
        file.write(response.content)
    # информация о том, когда файл загрузился и где был сохранён.
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    # Нашли pep
    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'numerical-index'}).find_all('tr')
    status_main = []
    status_on_pep_page = []
    # Ищем статус
    for row in main_div[1:4]:
        preview_status = find_tag(row, 'abbr').text[1:]
        status_main.append(preview_status)

    # Сравниваем статусы
    for row in main_div[1:4]:
        preview_status = find_tag(row, 'abbr').text[1:]
        version_a_tag = find_tag(row, 'a')['href']
        version_link = urljoin(PEP_URL, version_a_tag)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        # dl_tag_in_soup = find_tag(soup, 'abbr', {'title':'Currently valid informational guidance, or an in-use process'})


    return status_main





MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    """
    В словаре MODE_TO_FUNCTION функции парсера сопоставляются со строками.

    Которые в дальнейшем будут допустимыми значениями аргумента.
    Нужная функция вызывается по ключу: MODE_TO_FUNCTION[parser_mode]().
    На вызов указывают круглые скобки в конце выражения.
    """
    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')

    # Создание кеширующей сессии.
    session = requests_cache.CachedSession()
    # Если был передан ключ '--clear-cache', то args.clear_cache == True.
    if args.clear_cache:
        # Очистка кеша.
        session.cache.clear()
    # Получение из аргументов командной строки нужного режима работы.
    parser_mode = args.mode
    # Поиск и вызов нужной функции по ключу словаря.
    # С вызовом функции передаётся и сессия.
    results = MODE_TO_FUNCTION[parser_mode](session)
    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)

    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()


# ヽ(´▽`)/

# kaonashi
# =^..^=______/
