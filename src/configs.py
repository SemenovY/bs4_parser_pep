"""
Задаём режимы работы парсера через argparse.

Создайте в проекте новый файл configs.py — настроим в нём
парсер аргументов командной строки.
"""
import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import BASE_DIR, DT_FORMAT, LOG_FORMAT


# Конфигурация аргументов командной строки.
def configure_argument_parser(available_modes):
    """
    Аргумент mode — аргумент с режимами работы парсера.

    Это обязательный позиционный аргумент, а значит, его нужно обязательно
    указывать при запуске программы. Сами режимы работы заданы в
    параметре choices — они приходят из переменной available_modes,
    которая будет передаваться из файла main.py.
    Сейчас данные для парсинга берутся с сервера только при первом
    запуске программы. Потом работа ведётся через кеш. Когда понадобится
    свежая информация, придётся либо удалять файл с кешем, либо дописывать
    в код каждого парсера команды очистки кеша. Сложная схема.
    Упростим её с помощью аргументов командной строки.
    """
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file'),
        help='Дополнительные способы вывода данных'
    )
    parser.add_argument(
        '--pep',
        action='store_true',
        help='Страница pep'
    )
    return parser


#  Функция отвечает за конфигурацию логов.
def configure_logging():
    """
    В логи будет записываться время начала и окончания работы парсера.

    А также информация о том, какие аргументы командной строки
    были переданы при запуске программы.
    Для проекта parser_yap подойдёт глобальная настройка логов,
    сразу для всего проекта. Логи будут обрабатываться одинаково
    при записи из любого файла программы.
    В проекте parser_yap логи будут записываться с уровня INFO, то есть
    INFO, WARNING, ERROR и CRITICAL.
    Дополнительно нужно реализовать ротацию файлов через
    хендлер RotatingFileHandler. Он проследит за объёмом и
    количеством лог-файлов. Будем хранить одновременно не более пяти
    файлов с логами, каждый объёмом около одного мегабайта
    Также логи нужно вывести ещё и в терминал с помощью хендлера StreamHandler.
    """
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6, backupCount=5
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )


# ヽ(´▽`)/

# kaonashi
# =^..^=______/
