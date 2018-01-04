install-dev:
	pip3 install virtualenvwrapper
	export WORKON_HOME=$HOME/.virtualenvs
	export PROJECT_HOME=$HOME/WebDev
	export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3
	export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
	source /usr/local/bin/virtualenvwrapper.sh
	mkvirtualenv construbot
	cat $WORKON_HOME/construbot/bin/postactivate | sed -e 'construbot_root=~/WebDev/construbot/ \ncd $construbot_root \nPATH=$construbot_root/bin:$PATH'
	workon construbot
