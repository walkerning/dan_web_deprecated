run:
	gunicorn -k flask_sockets.worker --access-logfile _access_log.log --log-file _gunicorn_log.log --log-level debug dan_web.app:app

runmyvps:
	gunicorn -k flask_sockets.worker --access-logfile _access_log.log --log-file _gunicorn_log.log --log-level debug dan_web.app:app --bind 0.0.0.0:8002 -D

ready:
	@# 以后再来写自动部署, 包括依赖啥的

my-test-model:
	ipython -i test_model.py

clean-pyc:
	find . -name '*.pyc' | xargs -I{} rm {}
