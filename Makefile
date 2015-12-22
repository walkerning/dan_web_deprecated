run:
	gunicorn -k flask_sockets.worker dan_web.app:app

clean-pyc:
	find . -name '*.pyc' | xargs -I{} rm {}
