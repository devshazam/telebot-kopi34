# Generated by Django 5.0.7 on 2024-08-05 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telebot_15', '0002_teleorders'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Orders',
        ),
        migrations.AlterField(
            model_name='users',
            name='firstName',
            field=models.CharField(blank=True, max_length=255, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='users',
            name='lastName',
            field=models.CharField(blank=True, max_length=255, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='users',
            name='phone',
            field=models.CharField(blank=True, max_length=255, verbose_name='Телефон'),
        ),
    ]
