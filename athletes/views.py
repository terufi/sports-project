import os
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage

from .forms import AthleteForm, UploadFileForm
from .utils import (
    sanitize_filename,
    validate_json_file,
    validate_xml_file,
    save_athlete_to_json,
    save_athlete_to_xml,
    get_all_data_files,
    read_data_file,
)


def index(request):
    """Главная: список всех файлов и их содержимое."""
    files = get_all_data_files()
    files_data = []
    for filename in files:
        records, error = read_data_file(filename)
        files_data.append({
            'filename': filename,
            'records': records if records else [],
            'error': error,
        })
    return render(request, 'athletes/index.html', {
        'files_data': files_data,
        'has_files': len(files) > 0,
    })


def add_athlete(request):
    """Добавление спортсмена через форму."""
    if request.method == 'POST':
        form = AthleteForm(request.POST)
        if form.is_valid():
            athlete_data = {
                'name': form.cleaned_data['name'],
                'age': form.cleaned_data['age'],
                'sport': form.cleaned_data['sport'],
                'country': form.cleaned_data['country'],
                'achievements': form.cleaned_data.get('achievements', ''),
            }
            fmt = form.cleaned_data['file_format']
            try:
                if fmt == 'json':
                    filename = save_athlete_to_json(athlete_data)
                else:
                    filename = save_athlete_to_xml(athlete_data)
                messages.success(request, f'Данные сохранены в файл: {filename}')
                return redirect('athletes:index')
            except Exception as e:
                messages.error(request, f'Ошибка сохранения: {e}')
    else:
        form = AthleteForm()

    return render(request, 'athletes/add_athlete.html', {'form': form})


def upload_file(request):
    """Загрузка файла с валидацией."""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data['file']
            safe_name = sanitize_filename(uploaded.name)
            fs = FileSystemStorage(location=settings.DATA_DIR)
            saved_name = fs.save(safe_name, uploaded)
            file_path = os.path.join(settings.DATA_DIR, saved_name)

            if saved_name.lower().endswith('.json'):
                is_valid, error = validate_json_file(file_path)
            else:
                is_valid, error = validate_xml_file(file_path)

            if not is_valid:
                try:
                    os.remove(file_path)
                except OSError:
                    pass
                messages.error(request, f'Файл невалиден и был удалён: {error}')
            else:
                messages.success(request, f'Файл "{saved_name}" успешно загружен.')
            return redirect('athletes:index')
    else:
        form = UploadFileForm()

    return render(request, 'athletes/upload.html', {'form': form})