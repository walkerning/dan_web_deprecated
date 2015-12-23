run:
	gunicorn -k flask_sockets.worker --access-logfile _access_log.log --log-file _gunicorn_log.log --log-level debug dan_web.app:app

my-test-model:
	ipython -i test_model.py

clean-pyc:
	find . -name '*.pyc' | xargs -I{} rm {}
