env:
	virtualenv -p `which python3` env
	env/bin/python setup.py develop

run_dbs:
	docker run -d --name teeawards-influxdb -v `pwd`/data/influxdb:/var/lib/influxdb -p 8086:8086 influxdb:1.5.4
	docker run -d --name teeawards-mongodb -v `pwd`/data/mongo:/data/db -p 27017:27017 mongo:4.0.0
