run:
	gunicorn -k gevent --access-logfile _access_log.log --log-file _gunicorn_log.log --log-level debug dan_web.app:app

clean-pyc:
	find . -name '*.pyc' | xargs -I{} rm {}
