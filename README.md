# Sports Project — импорт/экспорт данных спортсменов

Django-приложение для ввода, хранения и отображения данных о спортсменах
с поддержкой форматов JSON и XML.

## Возможности

- Ввод данных спортсмена через HTML-форму
- Сохранение данных в JSON или XML
- Валидация вводимых данных (ФИО, возраст, вид спорта, страна)
- Загрузка готовых JSON/XML-файлов с проверкой валидности
- Автоматическое удаление невалидных файлов
- Санитайз имени загружаемого файла
- Отображение содержимого всех файлов на главной странице

## Стек

- Python 3.12
- Django 5.x
- Bootstrap 5.3
- SQLite

## Установка и запуск

```bash
git clone https://github.com/terufi/sports-project.git
cd sports-project

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
