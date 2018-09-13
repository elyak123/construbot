mkenv:
	@export WORKON_HOME=$HOME/.virtualenvs
	@export PROJECT_HOME=$HOME/WebDev
	@export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3
	@export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
	@python3 scripts/devinstall.py

shell:
	@docker-compose -f docker-compose-dev.yml run django python manage.py shell

up:
	@docker-compose -f docker-compose-dev.yml up -d

down:
	@docker-compose -f docker-compose-dev.yml down

buildev:
	@sed s/DJANGO_SETTINGS_MODULE=config.settings.production/DJANGO_SETTINGS_MODULE=config.settings.local/g .env | tee .env
	@docker-compose -f docker-compose-dev.yml up --build

buildprod:
	@sed s/DJANGO_SETTINGS_MODULE=config.settings.local/DJANGO_SETTINGS_MODULE=config.settings.production/g .env | tee .env
	@docker-compose -f docker-compose.yml up --build
clean:
	@docker rm $(shell docker ps -a -q) -f
	@docker rmi $(shell docker images -q) -f

test:
	@coverage run --source='.' manage.py test && coverage report
cleanhard: clean
	@docker volume prune -f