from django.urls import path
from . import views

app_name = 'athletes'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_athlete, name='add_athlete'),
    path('upload/', views.upload_file, name='upload_file'),
    path('ajax/search/', views.search_athletes, name='search_athletes'),
    path('delete/<int:pk>/', views.delete_athlete, name='delete_athlete'),
    path('edit/<int:pk>/', views.edit_athlete, name='edit_athlete'),
]