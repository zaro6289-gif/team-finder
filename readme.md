# TeamFinder

Веб-приложение для поиска участников pet-проектов. Вариант 2: навыки пользователей и фильтрация участников по навыкам.

## Запуск через Docker

Создайте файл `.env` в корне проекта:

DJANGO_SECRET_KEY=django-insecure-your-secret-key-here
DJANGO_DEBUG=True
POSTGRES_DB=teamfinder
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
TASK_VERSION=2

Затем выполните:

docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

Проект доступен по адресу http://localhost:8000

## Остановка

docker-compose down