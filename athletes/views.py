import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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
from .models import Athlete


def index(request):
    source = request.GET.get('source', 'files') 
    
    files_data = []
    db_athletes = []

    if source == 'db':
        db_athletes = Athlete.objects.all().order_by('-id')
    else:
        files = get_all_data_files()
        for filename in files:
            records, error = read_data_file(filename)
            files_data.append({
                'filename': filename,
                'records': records if records else [],
                'error': error,
            })

    return render(request, 'athletes/index.html', {
        'source': source,
        'files_data': files_data,
        'has_files': len(files_data) > 0,
        'db_athletes': db_athletes,
    })


def add_athlete(request):
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
            
            save_target = form.cleaned_data.get('save_target')
            
            if save_target == 'db':
                if Athlete.objects.filter(name=athlete_data['name'], sport=athlete_data['sport']).exists():
                    messages.error(request, f'Спортсмен {athlete_data["name"]} уже есть в базе!')
                else:
                    Athlete.objects.create(**athlete_data)
                    messages.success(request, f'Спортсмен {athlete_data["name"]} добавлен в базу данных.')
                    return redirect('athletes:index')
            
            elif save_target == 'file':
                fmt = form.cleaned_data.get('file_format', 'json')
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


def search_athletes(request):
    query = request.GET.get('q', '')
    if query:
        results = Athlete.objects.filter(name__icontains=query) | Athlete.objects.filter(sport__icontains=query)
    else:
        results = Athlete.objects.all().order_by('-id')
    
    data = []
    for a in results:
        data.append({
            'id': a.id,
            'name': a.name,
            'sport': a.sport,
            'age': a.age,
            'country': a.country,
            'achievements': a.achievements,
        })
    return JsonResponse({'results': data})    


def delete_athlete(request, pk):
    athlete = get_object_or_404(Athlete, pk=pk)
    if request.method == 'POST':
        athlete.delete()
        messages.success(request, 'Запись успешно удалена.')
    return redirect('/?source=db')


def edit_athlete(request, pk):
    athlete = get_object_or_404(Athlete, pk=pk)
    if request.method == 'POST':
        form = AthleteForm(request.POST)
        if form.is_valid():
            athlete.name = form.cleaned_data['name']
            athlete.age = form.cleaned_data['age']
            athlete.sport = form.cleaned_data['sport']
            athlete.country = form.cleaned_data['country']
            athlete.achievements = form.cleaned_data.get('achievements', '')
            athlete.save()
            messages.success(request, 'Данные спортсмена обновлены.')
            return redirect('/?source=db')
    else:
        form = AthleteForm(initial={
            'name': athlete.name,
            'age': athlete.age,
            'sport': athlete.sport,
            'country': athlete.country,
            'achievements': athlete.achievements,
            'save_target': 'db',
        })
    
    return render(request, 'athletes/edit_athlete.html', {'form': form, 'athlete': athlete})