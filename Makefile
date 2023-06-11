mkenv:
	@pip-compile --help > /dev/null
	@pip-sync requirements/local.txt

pipcompile:
	@pip-compile --help > /dev/null
	@pip-compile --resolver=backtracking --output-file requirements/base.txt
	@pip-compile --resolver=backtracking requirements/local.in --output-file requirements/local.txt
	@pip-compile --resolver=backtracking requirements/test.in --output-file requirements/test.txt

dockerenv:
	@sed -i.bak s/USE_DOCKER=no/USE_DOCKER=yes/g .env

shell: dockerenv
	@docker compose -f docker-compose-dev.yml run django python manage.py shell

poblar: dockerenv
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=construbot.config.settings.production/DJANGO_SETTINGS_MODULE=construbot.config.settings.local/g .env
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=construbot.config.settings.test/DJANGO_SETTINGS_MODULE=construbot.config.settings.local/g .env
	@docker compose -f docker-compose-dev.yml run django python manage.py poblar	

superuser: dockerenv
	@docker compose -f docker-compose-dev.yml run django python manage.py createsuperuser	

up: dockerenv
	@docker compose -f docker-compose-dev.yml up -d

down: dockerenv
	@docker compose -f docker-compose-dev.yml down

migrations: dockerenv
	@docker compose -f docker-compose-dev.yml run django python manage.py makemigrations
	@docker compose -f docker-compose-dev.yml run django python manage.py migrate

buildev: dockerenv
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=construbot.config.settings.production/DJANGO_SETTINGS_MODULE=construbot.config.settings.local/g .env
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=construbot.config.settings.test/DJANGO_SETTINGS_MODULE=construbot.config.settings.local/g .env
	@sed -i.bak s/DJANGO_DEBUG=False/DJANGO_DEBUG=True/g .env
	@docker compose -f docker-compose-dev.yml up --build

dev: dockerenv
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=construbot.config.settings.production/DJANGO_SETTINGS_MODULE=construbot.config.settings.local/g .env
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=construbot.config.settings.test/DJANGO_SETTINGS_MODULE=construbot.config.settings.local/g .env
	@sed -i.bak s/DJANGO_DEBUG=False/DJANGO_DEBUG=True/g .env
	@docker compose -f docker-compose-dev.yml up -d redis
	@docker compose -f docker-compose-dev.yml up -d postgres
	@docker compose -f docker-compose-dev.yml up -d mailhog
	@docker compose -f docker-compose-dev.yml run --service-ports django

buildprod: dockerenv
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=construbot.config.settings.local/DJANGO_SETTINGS_MODULE=construbot.config.settings.production/g .env
	@sed -i.bak s/DJANGO_DEBUG=True/DJANGO_DEBUG=False/g .env
	@docker compose -f docker-compose.yml up --build

test: dockerenv
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=construbot.config.settings.production/DJANGO_SETTINGS_MODULE=construbot.config.settings.test/g .env
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=construbot.config.settings.local/DJANGO_SETTINGS_MODULE=construbot.config.settings.test/g .env
	@docker compose -f docker-compose-dev.yml run --rm django coverage run --source='.' manage.py test
	@docker compose -f docker-compose-dev.yml run --rm django coverage report

warningtest: dockerenv
	@docker compose -f docker-compose-dev.yml run django python -Wa manage.py test

current: dockerenv
	@docker compose -f docker-compose-dev.yml run --rm django coverage run --source='.' manage.py test --tag=current

clean:
	@docker rm $(shell docker ps -a -q) -f

cleandb: clean
	@docker rmi $(shell docker images -q construbot_postgres) -f
	@docker volume rm $(shell docker volume ls -qf "name=construbot_postgres*")

cleanhard: clean
	@docker rmi $(shell docker images -q) -f
	@docker volume prune -f

runserver:
	@sed -i.bak s/USE_DOCKER=yes/USE_DOCKER=no/g .env
	@python manage.py runserver

localtest:
	@sed -i.bak s/USE_DOCKER=yes/USE_DOCKER=no/g .env
	@python manage.py test
