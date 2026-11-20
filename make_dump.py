import os
import django

# Настраиваем Django на старую базу SQLite
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# Принудительно переключаем на sqlite
from django.conf import settings
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': settings.BASE_DIR / 'db.sqlite3',
}

django.setup()

from django.core.management import call_command

# Выгружаем данные в JSON прямо через Python (он всегда пишет в UTF-8)
with open('db_data.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', 'athletes', indent=2, stdout=f)

print("Данные успешно выгружены в db_data.json в кодировке UTF-8!")