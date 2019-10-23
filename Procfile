web: gunicorn config.wsgi:application
worker: celery worker --app=construbot.taskapp --loglevel=info
