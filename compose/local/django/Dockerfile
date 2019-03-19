FROM python:3.6.8-alpine3.8

ENV PYTHONUNBUFFERED 1

COPY ./requirements /requirements
# Paquetes que se ocupan despues de hacer build
# bash se necesita para ejecutar start.sh y entrypoint.sh
# git se necesita despues para subir a coveralls
RUN apk add bash git

##
RUN apk add --no-cache --virtual .build-deps \
  build-base postgresql-dev gcc musl-dev jpeg-dev zlib-dev libffi-dev bash \
    && pip install pip-tools==3.1.0 \
    && pip-sync requirements/base.txt requirements/local.txt \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps
##

RUN apk add --update --no-cache \
    libgcc libstdc++ libx11 glib libxrender libxext libintl \
    libcrypto1.0 libssl1.0 \
    ttf-dejavu ttf-droid ttf-freefont ttf-liberation ttf-ubuntu-font-family wget


RUN wget -O /bin/wkhtmltopdf https://s3-us-west-2.amazonaws.com/elyak123-wkhtmltopdf/wkhtmltopdf
RUN chmod +x /bin/wkhtmltopdf

COPY ./compose/production/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY .coveragerc /.coveragerc
RUN sed -i 's/\r//' /.coveragerc
RUN chmod +x /.coveragerc

COPY ./compose/local/django/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh
RUN chmod +x /start.sh

COPY ./compose/local/django/celery/worker/start.sh /start-celeryworker.sh
RUN sed -i 's/\r//' /start-celeryworker.sh
RUN chmod +x /start-celeryworker.sh

COPY ./compose/local/django/celery/beat/start.sh /start-celerybeat.sh
RUN sed -i 's/\r//' /start-celerybeat.sh
RUN chmod +x /start-celerybeat.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
