# Generated by Django 3.2 on 2024-05-13 16:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('measurement_unit', models.CharField(choices=[('мл', 'Миллилитр'), ('г', 'Грамм'), ('ч. л.', 'Чайная ложка'), ('ст. л.', 'Столовая ложка'), ('шт.', 'Штука'), ('капля', 'Капля'), ('кусок', 'Кусок'), ('банка', 'Банка'), ('щепотка', 'Щепотка'), ('горсть', 'Горсть'), ('батон', 'Батон'), ('веточка', 'Веточка'), ('стакан', 'Стакан')], max_length=10, verbose_name='Единицы измерения')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('image', models.ImageField(upload_to='media', verbose_name='Картинка')),
                ('text', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время приготовления')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
                ('slug', models.SlugField(verbose_name='Slug')),
            ],
        ),
    ]