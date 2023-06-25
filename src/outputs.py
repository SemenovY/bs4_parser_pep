"""
Файл отвечает за вывод данных.

Чтобы данные вывелись в формате таблицы, нужно будет просто указать этот
аргумент при запуске программы через терминал.
Если он будет пропущен, то информация распечатается как обычно.

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

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


# Контроль вывода результатов парсинга.
def control_output(results, cli_args):
    """
    Анализирует атрибуты, указанные при запуске программы.
    По ним определяет, в каком виде нужно предоставить данные.
    """
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


# Вывод данных в терминал построчно.
def default_output(results):
    """Вывод данных по умолчанию (построчно)."""
    for row in results:
        print(*row)


# Вывод данных в формате PrettyTable.
def pretty_output(results):
    """Печать данных в формате таблицы."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


# Создание директории и файла с результатами парсинга.
def file_output(results, cli_args):
    """
    Нужно создать ещё одну директорию с результатами парсинга — results.

    В случае с проектом parser_yap по названию файлов с результатами парсинга
    должно быть понятно, когда был сохранён файл, чтобы можно было сравнивать
    документы за разные промежутки времени. Также важно, чтобы в
    названии отражалось, в каком режиме работала программа — whats-new
    или latest-versions. Значит, для названия файла подойдёт такой
    формат: «режим работы программы» + «дата и время записи» + формат (csv).
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
