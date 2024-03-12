from django.db import models
from django.utils.timezone import now


class Location(models.Model):
    address = models.CharField(
        verbose_name='Адрес',
        max_length=100,
        unique=True,
    )
    lat = models.FloatField(
        verbose_name="Широта",
        null=True,
        blank=True,
    )
    lon = models.FloatField(
        verbose_name="Долгота",
        null=True,
        blank=True,
    )
    last_update = models.DateTimeField(
        verbose_name="Последнее обновление",
        default=now,
    )

    class Meta:
        verbose_name = 'локация'
        verbose_name_plural = 'локации'

    def __str__(self):
        return self.address
