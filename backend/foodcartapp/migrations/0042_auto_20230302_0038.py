# Generated by Django 3.2.15 on 2023-03-02 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_auto_20230301_2358'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(default='', max_length=500, verbose_name='комментарий к заказу'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('MR', 'У менеджера'), ('RT', 'В ресторане'), ('CR', 'У курьера'), ('CT', 'Доставлен')], db_index=True, default='MR', max_length=10, verbose_name='статус'),
        ),
    ]
