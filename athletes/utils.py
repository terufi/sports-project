import json
import os
import re
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from django.conf import settings


def sanitize_filename(filename):
    """Генерирует безопасное уникальное имя файла."""
    filename = os.path.basename(filename)
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^\w\-]', '_', name)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique = uuid.uuid4().hex[:8]
    ext = ext.lower()
    if ext not in ('.json', '.xml'):
        ext = '.json'
    return f"{name}_{timestamp}_{unique}{ext}"


def validate_athlete_data(data):
    """Проверяет структуру данных спортсмена."""
    if not isinstance(data, dict):
        return False, 'Данные должны быть объектом.'

    for field in ['name', 'age', 'sport', 'country']:
        if field not in data:
            return False, f'Отсутствует обязательное поле: {field}'

    if not isinstance(data['name'], str) or len(data['name'].strip()) < 2:
        return False, 'Некорректное поле ФИО (name) — минимум 5 символов.'
    if not isinstance(data['age'], int) or not (10 <= data['age'] <= 100):
        return False, 'Некорректное поле age (10..100).'
    if not isinstance(data['sport'], str) or len(data['sport'].strip()) < 2:
        return False, 'Некорректное поле sport.'
    if not isinstance(data['country'], str) or len(data['country'].strip()) < 2:
        return False, 'Некорректное поле country.'

    return True, ''


def validate_json_file(file_path):
    """Проверка JSON-файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return False, f'Ошибка чтения JSON: {e}'

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return False, 'JSON должен содержать объект или массив.'
    if not data:
        return False, 'Файл пустой.'

    for i, item in enumerate(data):
        ok, err = validate_athlete_data(item)
        if not ok:
            return False, f'Запись #{i + 1}: {err}'
    return True, ''


def validate_xml_file(file_path):
    """Проверка XML-файла."""
    try:
        tree = ET.parse(file_path)
    except ET.ParseError as e:
        return False, f'Ошибка парсинга XML: {e}'

    root = tree.getroot()
    if root.tag != 'athletes':
        return False, 'Корневой элемент должен быть <athletes>.'

    items = list(root.findall('athlete'))
    if not items:
        return False, 'Файл не содержит <athlete>.'

    for i, item in enumerate(items):
        data = {child.tag: child.text for child in item}
        try:
            data['age'] = int(data.get('age', ''))
        except (ValueError, TypeError):
            return False, f'Запись #{i + 1}: age должен быть числом.'

        ok, err = validate_athlete_data(data)
        if not ok:
            return False, f'Запись #{i + 1}: {err}'
    return True, ''


def save_athlete_to_json(athlete_data):
    """Сохраняет в новый JSON-файл."""
    filename = sanitize_filename(f"athlete_{athlete_data['name']}.json")
    file_path = os.path.join(settings.DATA_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([athlete_data], f, ensure_ascii=False, indent=2)
    return filename


def save_athlete_to_xml(athlete_data):
    """Сохраняет в новый XML-файл."""
    filename = sanitize_filename(f"athlete_{athlete_data['name']}.xml")
    file_path = os.path.join(settings.DATA_DIR, filename)

    root = ET.Element('athletes')
    athlete_el = ET.SubElement(root, 'athlete')
    for key, value in athlete_data.items():
        child = ET.SubElement(athlete_el, key)
        child.text = str(value) if value is not None else ''

    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')
    tree.write(file_path, encoding='utf-8', xml_declaration=True)
    return filename


def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    return data


def read_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    result = []
    for item in root.findall('athlete'):
        result.append({child.tag: child.text for child in item})
    return result


def get_all_data_files():
    """Список всех JSON/XML файлов в data/."""
    if not os.path.isdir(settings.DATA_DIR):
        return []
    return sorted([
        name for name in os.listdir(settings.DATA_DIR)
        if name.lower().endswith(('.json', '.xml'))
    ])


def read_data_file(filename):
    """Читает файл по имени. Возвращает (records, error)."""
    file_path = os.path.join(settings.DATA_DIR, filename)
    if not os.path.isfile(file_path):
        return None, 'Файл не найден.'

    try:
        if filename.lower().endswith('.json'):
            return read_json_file(file_path), ''
        elif filename.lower().endswith('.xml'):
            return read_xml_file(file_path), ''
        return None, 'Неподдерживаемый формат.'
    except Exception as e:
        return None, f'Ошибка чтения: {e}'