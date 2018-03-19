#!/usr/bin/env python
import os
import sys
import environ

ROOT_DIR = environ.Path(__file__) - 1
env = environ.Env()
# .env file, should load only in development environment
READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)

if __name__ == "__main__":
    if READ_DOT_ENV_FILE:
        # Operating System Environment variables have precedence over variables defined in the .env file,
        # that is to say variables from the .env files will only be used if not defined
        # as environment variables.
        env_file = str(ROOT_DIR.path('.env'))
        env.read_env(env_file)
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE",
            env('DJANGO_SETTINGS_MODULE', default='')
        )
    else:
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE", "config.settings.production"
        )
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise

    # This allows easy placement of apps within the interior
    # construbot directory.
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_path, 'construbot'))

    execute_from_command_line(sys.argv)
