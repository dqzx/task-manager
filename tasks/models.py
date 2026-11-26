from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('normal', 'Обычный'),
        ('high', 'Высокий'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')
    title = models.CharField(max_length=200, verbose_name='Краткое название')
    description = models.TextField(blank=True, verbose_name='Подробное описание')
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Срок выполнения')
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name='Приоритет',
    )
    completed = models.BooleanField(default=False, verbose_name='Выполнена')

    def __str__(self):
        return self.title
