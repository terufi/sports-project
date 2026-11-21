# Sports Project — импорт/экспорт данных спортсменов

Django-приложение для ввода, хранения и отображения данных о спортсменах с поддержкой форматов JSON и XML, а также реляционных баз данных (SQLite / PostgreSQL). На текущем этапе проект полностью контейнеризирован.

## Возможности
- Ввод данных спортсмена через HTML-форму
- Выбор источника сохранения: в файл (JSON или XML) или в базу данных
- Проверка на дубликаты при сохранении в БД
- Валидация вводимых данных (ФИО, возраст, вид спорта, страна)
- Загрузка готовых JSON/XML-файлов с проверкой валидности
- Автоматическое удаление невалидных файлов
- Санитайз имени загружаемого файла
- Отображение содержимого всех файлов и записей из БД на главной странице
- AJAX-поиск по базе данных (без перезагрузки страницы)
- Редактирование и удаление записей из БД
- Адаптивный интерфейс на Bootstrap 5

## Стек
- Python 3.12
- Django 6.1
- Bootstrap 5.3
- SQLite (локальная разработка)
- PostgreSQL 15 (Docker)
- Docker, Docker Compose

## Запуск через Docker (с PostgreSQL)

Для запуска проекта необходим установленный и запущенный Docker Desktop.

1. Создайте файл `.env` в корне проекта (он добавлен в `.gitignore`):

SECRET_KEY=ваш_секретный_ключ_django
DEBUG=True
ALLOWED_HOSTS=*
DB_NAME=sports_db
DB_USER=sports_user
DB_PASSWORD=super_secret_password
DB_HOST=db
DB_PORT=5432

2. Соберите и запустите контейнеры:

docker compose up -d --build

3. Примените миграции для создания таблиц в PostgreSQL:

docker compose exec web python manage.py migrate

4. Приложение доступно по адресу: http://127.0.0.1:8000/

(Чтобы остановить контейнеры, выполните: docker compose down)

## Миграция данных из SQLite в PostgreSQL
Если нужно перенести данные из старой локальной базы SQLite в новую PostgreSQL:

1. Выгрузите данные: python manage.py dumpdata athletes --indent 2 -o db_data.json
2. Скопируйте и загрузите в Docker:

docker compose cp db_data.json web:/app/
docker compose exec web python manage.py loaddata db_data.json

## Установка и запуск (без Docker, SQLite)

Если необходимо запустить проект без Docker (на SQLite):

git clone https://github.com/terufi/sports-project.git
cd sports-project

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver