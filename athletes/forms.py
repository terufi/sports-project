import re
from django import forms


class AthleteForm(forms.Form):
    """Форма для ввода данных о спортсмене."""
    name = forms.CharField(
        max_length=100,
        label='ФИО спортсмена',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'})
    )
    age = forms.IntegerField(
        min_value=10,
        max_value=100,
        label='Возраст',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '25'})
    )
    sport = forms.CharField(
        max_length=100,
        label='Вид спорта',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Плавание'})
    )
    country = forms.CharField(
        max_length=100,
        label='Страна',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Россия'})
    )
    achievements = forms.CharField(
        required=False,
        label='Достижения',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Олимпийский чемпион 2020'})
    )
    file_format = forms.ChoiceField(
        choices=[('json', 'JSON'), ('xml', 'XML')],
        label='Формат файла',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not re.match(r'^[А-Яа-яЁёA-Za-z\s\-]+$', name):
            raise forms.ValidationError('ФИО должно содержать только буквы, пробелы и дефисы.')
        if len(name) < 5:
            raise forms.ValidationError('ФИО слишком короткое (минимум 5 символов).')
        return name


class UploadFileForm(forms.Form):
    """Форма для загрузки файла с данными."""
    file = forms.FileField(
        label='Файл (JSON или XML)',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.json,.xml'})
    )

    def clean_file(self):
        f = self.cleaned_data['file']
        if not f.name.lower().endswith(('.json', '.xml')):
            raise forms.ValidationError('Допускаются только файлы JSON или XML.')
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Размер файла не должен превышать 5 МБ.')
        return f