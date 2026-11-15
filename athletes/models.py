from django.db import models

class Athlete(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    sport = models.CharField(max_length=100, verbose_name="Вид спорта")
    age = models.IntegerField(verbose_name="Возраст")
    country = models.CharField(max_length=100, verbose_name="Страна")
    achievements = models.TextField(blank=True, verbose_name="Достижения")

    def __str__(self):
        return self.name
