run:
	gunicorn -k flask_sockets.worker --access-logfile _access_log.log --log-file _gunicorn_log.log --log-level debug dan_web.app:app

runwithnginx:
	gunicorn -k flask_sockets.worker --access-logfile _access_log.log --log-file _gunicorn_log.log --log-level debug dan_web.app:app --bind localhost:8002 -D

runmyvps:
	gunicorn -k flask_sockets.worker --access-logfile _access_log.log --log-file _gunicorn_log.log --log-level debug dan_web.app:app --bind 0.0.0.0:8002 -D

runnod:
	gunicorn -k flask_sockets.worker --access-logfile - --log-level debug dan_web.app:app --bind 0.0.0.0:8003

ready:
	@# 以后再来写自动部署, 包括依赖啥的
	@# 其实不该写在这里...
	mkdir -p dan_web/uploads/
	mkdir -p dan_web/user_confs/
	mkdir -p dan_web/user_logs/
	mkdir -p /tmp/dan_web/tmp_conf

my-test-model:
	ipython -i test_model.py

clean-pyc:
	find . -name '*.pyc' | xargs -I{} rm {}
