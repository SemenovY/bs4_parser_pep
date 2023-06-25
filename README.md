# Парсер документации Python и PEP
## Описание
Парсер информации о Python с **https://docs.python.org/3/** и **https://peps.python.org/**
### Перед использованием
Клонируйте репозиторий к себе на компьютер при помощи команд:
```
git clone https://github.com/SemenovY/bs4_parser_pep
```
или
```
git clone git@github.com:https:SemenovY/bs4_parser_pep
```
или
```
git clone gh repo clone SemenovY/bs4_parser_pep
```

В корневой папке нужно создать виртуальное окружение и установить зависимости.
```
python -m venv venv
```
```
pip install -r requirements.txt
```
### смените директорию на папку ./src/
```
cd src/
```
### запустите файл main.py выбрав необходимый парсер и аргументы
```
python main.py [вариант парсера] [аргументы]
```
### Встроенные парсеры
- whats-new   
Парсер выводящий список изменений в Python.
```
python main.py whats-new [аргументы]
```
- latest_versions  
Парсер выводящий список версий Python и ссылки на их документацию.
```
python main.py latest-versions [аргументы]
```
- download  
Парсер будет скачивать архив с документацией Python на локальный диск.
```
python main.py download [аргументы]
```
- pep  
Парсер выводящий список статусов документов pep
и количество документов в каждом статусе. 
```
python main.py pep [аргументы]
```
### Аргументы
Есть возможность указывать аргументы для изменения работы программы:   
- -h, --help  
Общая информация о командах.
```
python main.py -h
```
- -c, --clear-cache  
Очистка кеша перед выполнением парсинга.
```
python main.py [вариант парсера] -c
```
- -o {pretty,file}, --output {pretty,file}   
Дополнительные способы вывода данных   
pretty - выводит данные в командной строке в таблице   
file - сохраняет информацию в формате csv в папке ./results/
```
python main.py [вариант парсера] -o file
```
### Автор
- Семёнов Юрий -  [GitHub](https://github.com/SemenovY ) 
---
### kaonashi
### =^..^=______/
