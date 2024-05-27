import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = ('Загрузка данных из csv-файлов в модель Ingredient. ',
            'Пример команды: python manage.py import_data')

    def handle(self, *args, **options):
        csv_file_path = 'data/ingredients.csv'
        model = Ingredient
        self.import_data(model, csv_file_path)

    def import_data(self, model, csv_file_path):
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name = row[0]
                measurement_unit = row[1]
                data = {'name': name, 'measurement_unit': measurement_unit}
                # Распаковываем словарь и создаем объект модели
                model.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Successfully imported data'))
