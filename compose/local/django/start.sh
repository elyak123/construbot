#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

export DJANGO_READ_DOT_ENV_FILE=True
export USE_DOCKER=yes
python manage.py migrate
#python manage.py test
python manage.py runserver_plus 0.0.0.0:8343