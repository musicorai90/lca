# Generated by Django 3.2.5 on 2021-07-18 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20210717_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='horario',
            name='hora_fin',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='horario',
            name='hora_inicio',
            field=models.TimeField(),
        ),
    ]