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
    python_requires='>=3.9.17',
    install_requires=[
        # Conservative Django
        'django[argon2]==3.2.19',
        # REST
        'djangorestframework==3.13.1',
        'djangorestframework_simplejwt==5.2.0',
        # Configuration
        'django-environ==0.9.0',
        'whitenoise==6.4.0',
        # Models
        'django-model-utils==4.2.0',
        'django-treebeard==4.5.1',
        # Images
        'Pillow>=9.2.0',
        # For user registration, either via email or social
        # Well-built with regular release cycles!
        'django-allauth==0.51.0',
        # Python-PostgreSQL Database Adapter
        'psycopg2==2.8.6',
        # Unicode slugification
        'awesome-slugify==1.6.5',
        # Time zones support
        'pytz==2022.1',
        # Redis support
        'django-redis==5.2.0',
        'redis==3.2.1',
        # Celery support
        'celery==5.2.7',
        # Compressing static files
        'rcssmin==1.1.0',
        'django-compressor==4.0',
        # FrontEnd Libraries
        'django-autocomplete-light==3.9.4',
        'django-bootstrap4==22.1',
        # xls files handling
        'openpyxl==2.6.2',
        # WSGI Handler
        # ------------------------------------------------
        'gunicorn==19.7.1',

        # Static and Media Storage
        # ------------------------------------------------
        'django-storages[boto3]==1.13.2',
        # Email backends for Mailgun, Postmark, SendGrid and more
        # -------------------------------------------------------
        'django-anymail>=10.0,<11.0',
        # --------------------------
        # Sentry client
        'sentry-sdk>=1.14.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
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
