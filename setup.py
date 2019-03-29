import os
import re
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('construbot')

setup(
    name='django-construbot',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license='GNU Affero General Public License v3',
    description='Una Solucion operativa para constructoras.',
    long_description=README,
    url='https://www.construbot.com.mx/',
    author='Javier Llamas Ramirez',
    author_email='elyak.123@gmail.com',
    python_requires='>=3.6.1',
    install_requires=[
        # Conservative Django
        'django>=1.11.19, <2.0',
        # REST
        'djangorestframework==3.8.2',
        'djangorestframework-jwt==1.11.0',
        # Configuration
        'django-environ==0.4.4',
        'whitenoise==3.3.1',
        # Models
        'django-model-utils==3.1.1',
        # Images
        'Pillow==5.0.0',
        # Password storage
        'argon2-cffi==18.1.0',
        # For user registration, either via email or social
        # Well-built with regular release cycles!
        'django-allauth==0.34.0',
        # Python-PostgreSQL Database Adapter
        'psycopg2>=2.7,<2.8',
        # Unicode slugification
        'awesome-slugify==1.6.5',
        # Time zones support
        'pytz==2017.3',
        # Redis support
        'django-redis==4.10.0',
        'redis==3.2.1',
        # Celery support
        'celery==4.2.1',
        #'kombu==4.4.0',
        # Compressing static files
        'rcssmin==1.0.6 ',
        'django-compressor==2.2',
        # PDF Generation
        'django-wkhtmltopdf==3.2.0',
        # FrontEnd Libraries
        'django-autocomplete-light==3.2.10',
        'django-bootstrap4==0.0.6',
        # WSGI Handler
        # ------------------------------------------------
        'gunicorn==19.7.1',

        # Static and Media Storage
        # ------------------------------------------------
        'boto3==1.9.28',
        'django-storages==1.7.1',
        # Email backends for Mailgun, Postmark, SendGrid and more
        # -------------------------------------------------------
        'django-anymail==1.4',
        # Sentry client
        # --------------------------
        'sentry-sdk==0.7.6',
        # Security
        'pyup-django==0.4.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3'
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
