# Generated by Django 3.2.5 on 2021-07-17 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_reporte_fecha_inicio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permiso',
            name='imagen',
            field=models.ImageField(upload_to='media/recipes'),
        ),
    ]
