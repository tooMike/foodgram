# Generated by Django 3.2 on 2024-05-21 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('url_shortener', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shorturl',
            options={'verbose_name': 'короткая ссылка', 'verbose_name_plural': 'Короткие ссылки'},
        ),
    ]