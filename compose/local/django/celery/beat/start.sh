#!/bin/sh

set -o errexit
set -o nounset



rm -f './celerybeat.pid'
celery -A construbot.taskapp beat -l INFO
