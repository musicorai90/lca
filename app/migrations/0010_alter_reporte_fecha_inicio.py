# Generated by Django 3.2.5 on 2021-07-17 08:22

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20210717_0420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reporte',
            name='fecha_inicio',
            field=models.DateField(default=datetime.datetime(2021, 7, 17, 8, 22, 16, 444779, tzinfo=utc)),
        ),
    ]
