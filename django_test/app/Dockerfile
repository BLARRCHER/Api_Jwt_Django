FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY run_uwsgi.sh run_uwsgi.sh
COPY requirements.txt requirements.txt
COPY wait_for_it.sh wait_for_it.sh
COPY uwsgi/uwsgi.ini uwsgi.ini

RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install -r requirements.txt \
     && sed $'s/\r$//' ./wait_for_it.sh > ./wait_for_it.unix.sh \
     && chmod +x wait_for_it.unix.sh

COPY . .

EXPOSE 8000

RUN python manage.py makemigrations --name project_init_migration \
    && python manage.py collectstatic


ENTRYPOINT bash ./wait_for_it.unix.sh service_db:5432 -- uwsgi --strict --ini uwsgi.ini