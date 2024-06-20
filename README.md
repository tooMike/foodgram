# Описание

Проект FoodGram позволяет пользователям делиться своими и просматривать рецепты других пользователей. 

Использован Django REST Framework для создания REST API, обеспечивающего взаимодействие с базой данных PostgreSQL и аутентификацию с помощью токенов через Djoser. Проект подготовлен к развертыванию на сервере с использованием Docker контейнеров и оркестрации Docker Compose. Добавлена функциональность для импорта данных в БД из JSON-файлов. 

Реализован процесс CI/CD с помощью GitHub Actions (активация происходит при push в ветку releases). При успешном деплое на сервер происходит отправка сообщения в Telegram.

Запущенный проект с тестовыми данными доступен по адресу: https://jtt365.com/

Документация к API достпуна по адресу: https://jtt365.com/api/docs/

# Авторы проекта

[Mikhail](https://github.com/tooMike)

# Установка и запуск с Docker

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/tooMike/foodgram
```

```
cd foodgram
```

Запустить сборку проекта:

```
docker compose up
```

Выполнить сбор статики в контейнере backend:

```
docker compose exec backend python manage.py collectstatic
```

Выполнить миграции в контейнере backend:

```
docker compose exec backend python manage.py migrate
```

Проект будет доступен по адресу

```
http://127.0.0.1:10000/
```

# Добавление тестовых данных (пользователи, ингредиенты, теги, рецепты)

Выполнить команду import_data в контейнере backend:

```
docker compose exec backend python manage.py import_data
```

# Спецификация

При локальном запуске документация будет доступна по адресу:

```
http://127.0.0.1:10000/api/docs/
```

# Примеры запросов к API

### Регистрация нового пользователя

Описание метода: Зарегистрировать пользователя в сервисе. Права доступа: Доступно без токена.

Тип запроса: `POST`

Эндпоинт: `/api/users/`

Обязательные параметры: `email, username, first_name, last_name, password`

Пример запрос:

```
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Иванов",
  "password": "Qwerty123"
}
```

Пример успешного ответа:

```
{
  "email": "vpupkin@yandex.ru",
  "id": 0,
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Иванов"
}
```

### Cписок тегов

Описание метода: Получение списка тегов. Права доступа: Доступно без токена.

Тип запроса: `GET`

Эндпоинт: `/api/tags/`

Пример запроса:

Пример успешного ответа:

```
[
  {
    "id": 0,
    "name": "Завтрак",
    "slug": "breakfast"
  }
]
```

### Добавление нового рецепта

Описание метода: Добавить новый рецепт. Права доступа: Аутентифицированные пользователи.

Тип запроса: `POST`

Эндпоинт: `/api/recipes/`

Обязательные параметры: `ingredients, tags, image, name, text, cooking_time`

Пример запроса:

```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Пример успешного ответа:

```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```
