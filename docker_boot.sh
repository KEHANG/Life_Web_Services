#!/bin/bash
source activate lws_env
flask db upgrade
flask translate compile
exec gunicorn -b :5000 --access-logfile - --error-logfile - run:lws_app