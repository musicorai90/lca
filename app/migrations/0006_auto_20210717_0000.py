# Generated by Django 3.2.5 on 2021-07-17 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_personal_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='alumno',
            name='correo',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='personal',
            name='correo',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='personal',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='media/perfiles'),
        ),
    ]