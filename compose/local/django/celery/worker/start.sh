#!/bin/sh

set -o errexit
set -o nounset



celery -A construbot.taskapp worker -l INFO
