# Api_Jwt_Django
no drf

## Инструкция по запуску

1. Просмотреть/заменить переменные окружения в .env
2. Перейти в каталог django_test, запустить docker-compose up --build
3. Создать схему content в бд
4. Мигрировать данные из django (python manage.py migrate), создать суперпользователя (python manage.py createsuperuser).

Создавать пользователей, статьи можно как по API, так и в админке
