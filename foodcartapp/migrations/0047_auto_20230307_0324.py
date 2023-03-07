# Generated by Django 3.2.15 on 2023-03-07 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_order_restaurant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('NONE', 'Не выбран'), ('CASH', 'Наличные'), ('CARD', 'Карта'), ('ONLINE', 'На сайте')], db_index=True, default='NONE', max_length=10, verbose_name='способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('MANAGER', 'Согласование'), ('RESTAURANT', 'Готовится'), ('COURIER', 'В пути'), ('CLIENT', 'Доставлен')], db_index=True, default='MANAGER', max_length=10, verbose_name='статус'),
        ),
    ]
