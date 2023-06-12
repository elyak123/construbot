FROM python:3.9.17-alpine3.18

ENV PYTHONUNBUFFERED 1

ARG SETUPTOOLS_VERSION=65.5.1
ARG PIP_VERSION=23.1.2
ARG PIP_TOOLS_VERSION=6.13.0

RUN addgroup -S django && adduser -S -G django django

# Solo en caso de usar python alpine
RUN apk add bash

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
##
RUN apk add --no-cache --virtual .build-deps \
  build-base postgresql-dev gcc musl-dev jpeg-dev zlib-dev libffi-dev bash git \
    && pip install --upgrade pip==${PIP_VERSION} \
    && pip install setuptools>=${SETUPTOOLS_VERSION} \
    && pip install pip-tools==${PIP_TOOLS_VERSION} \
    && pip-sync requirements/base.txt \
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

COPY ./compose/production/django/gunicorn.sh /gunicorn.sh
RUN sed -i 's/\r//' /gunicorn.sh
RUN chmod +x /gunicorn.sh
RUN chown django /gunicorn.sh

COPY ./compose/production/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN chown django /entrypoint.sh

COPY ./compose/production/django/celery/worker/start.sh /start-celeryworker.sh
RUN sed -i 's/\r//' /start-celeryworker.sh
RUN chmod +x /start-celeryworker.sh

COPY ./compose/production/django/celery/beat/start.sh /start-celerybeat.sh
RUN sed -i 's/\r//' /start-celerybeat.sh
RUN chmod +x /start-celerybeat.sh

COPY . /app

RUN chown -R django /app

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
