# Generated by Django 3.2 on 2024-05-21 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20240521_1317'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipes', 'ordering': ('-created_at',), 'verbose_name': 'рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
    ]