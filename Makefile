install-dev:
	@export WORKON_HOME=$HOME/.virtualenvs
	@export PROJECT_HOME=$HOME/WebDev
	@export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3
	@export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
	@python3 scripts/devinstall.py


