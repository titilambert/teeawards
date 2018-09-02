env:
	virtualenv -p `which python3` env
	env/bin/python setup.py develop
