from django.db import models


class Location(models.Model):
    address = models.CharField(
        verbose_name='Адрес',
        max_length=100,
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
