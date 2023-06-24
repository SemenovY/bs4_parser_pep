"""
Создайте файл outputs.py; в нём будет находиться весь код.

Который отвечает за вывод данных:
Чтобы данные вывелись в формате таблицы, нужно будет просто указать этот
аргумент при запуске программы через терминал. Если он будет пропущен,
то информация распечатается как обычно.

Контролировать вывод результатов в программе будет
функция control_output(). У функции будет два параметра:
results — список с результатами results из функции main() файла main.py;
cli_args — объект с аргументами командной строки.
За печать данных в формате таблицы будет отвечать функция pretty_output(),
а за вывод данных по умолчанию (построчно) — функция default_output().

"""


import csv
import datetime as dt
import logging

from prettytable.colortable import ColorTable, Themes

from constants import BASE_DIR, DATETIME_FORMAT


# Контроль вывода результатов парсинга.
def control_output(results, cli_args):
    """
    Анализирует атрибуты, указанные при запуске программы.
    По ним определяет, в каком виде нужно предоставить данные.
    """
    CHOICES = {
        'pretty': pretty_output,
        'file': file_output,
        None: default_output
    }

    CHOICES[cli_args.output](results, cli_args)
    # """Контролировать вывод результатов в программе."""
    # # Чтобы не обращаться дважды к атрибуту объекта в условиях if, elif,
    # # сохраним значение в переменную.
    # output = cli_args.output
    #
    # if output == 'pretty':
    #     # Вывод данных в PrettyTable.
    #     pretty_output(results)
    # elif output == 'file':
    #     # Вывод данных в файл csv. Саму функцию напишем позже.
    #     file_output(results, cli_args)
    # else:
    #     # Вывод данных по умолчанию — в терминал построчно.
    #     default_output(results)


# Вывод данных в терминал построчно.
def default_output(results):
    """Вывод данных по умолчанию (построчно)."""
    for row in results:
        print(*row)


# Вывод данных в формате PrettyTable.
def pretty_output(results):
    """Печать данных в формате таблицы."""
    # Инициализируем объект PrettyTable.
    table = ColorTable(theme=Themes.OCEAN)
    # В качестве заголовков устанавливаем первый элемент списка.
    table.field_names = results[0]
    # Выравниваем всю таблицу по левому краю.
    table.align = 'l'
    # Добавляем все строки, начиная со второй (с индексом 1).
    table.add_rows(results[1:])
    # Печатаем таблицу.
    print(' ', table, ' ', '=^..^=______/', sep='\n')


# Создание директории и файла с результатами парсинга.
def file_output(results, cli_args):
    """
    Теперь нужно создать ещё одну директорию с результатами парсинга — results.

    Названия файлов
    В случае с проектом parser_yap по названию файлов с результатами парсинга
    должно быть понятно, когда был сохранён файл, чтобы можно было сравнивать
    документы за разные промежутки времени. Также важно, чтобы в
    названии отражалось, в каком режиме работала программа — whats-new
    или latest-versions. Значит, для названия файла подойдёт такой
    формат: «режим работы программы» + «дата и время записи» + формат (csv).
    Чтобы сформировать такое название, нужно получить режим работы
    парсера из аргументов командной строки и добавить к нему дату и
    время записи с помощью метода strftime() модуля datetime.
    """
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')


# ヽ(´▽`)/

# kaonashi
# =^..^=______/
