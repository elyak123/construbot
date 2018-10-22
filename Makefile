mkenv:
	@pip-compile --help > /dev/null
	@pip-sync requirements/base.txt requirements/local.txt

pipcompile:
	 @pip-compile --help > /dev/null
	 @pip-compile --generate-hashes --output-file requirements/base.txt
	 @pip-compile --generate-hashes requirements/local.in --output-file requirements/local.txt

shell:
	@docker-compose -f docker-compose-dev.yml run django python manage.py shell

poblar:
	@docker-compose -f docker-compose-dev.yml run django python manage.py poblar	

up:
	@docker-compose -f docker-compose-dev.yml up -d

down:
	@docker-compose -f docker-compose-dev.yml down

buildev:
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=config.settings.production/DJANGO_SETTINGS_MODULE=config.settings.local/g .env
	@sed -i.bak s/DJANGO_DEBUG=False/DJANGO_DEBUG=True/g .env
	@docker-compose -f docker-compose-dev.yml up --build

dev:
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=config.settings.production/DJANGO_SETTINGS_MODULE=config.settings.local/g .env
	@sed -i.bak s/DJANGO_DEBUG=False/DJANGO_DEBUG=True/g .env
	@docker-compose -f docker-compose-dev.yml up -d redis
	@docker-compose -f docker-compose-dev.yml up -d postgres
	@docker-compose -f docker-compose-dev.yml up -d mailhog
	@docker-compose -f docker-compose-dev.yml run --service-ports django

buildprod:
	@sed -i.bak s/DJANGO_SETTINGS_MODULE=config.settings.local/DJANGO_SETTINGS_MODULE=config.settings.production/g .env
	@sed -i.bak s/DJANGO_DEBUG=True/DJANGO_DEBUG=False/g .env
	@docker-compose -f docker-compose.yml up --build
clean:
	@docker rm $(shell docker ps -a -q) -f

test:
	@docker-compose -f docker-compose-dev.yml run --rm django coverage run --source='.' manage.py test
	@docker-compose -f docker-compose-dev.yml run --rm django coverage report

current:
	@docker-compose -f docker-compose-dev.yml run --rm django coverage run --source='.' manage.py test --tag=current

cleanhard: clean
	@docker rmi $(shell docker images -q) -f
	@docker volume prune -f