export FLASK_APP=run.py
source activate lws_env
flask db upgrade
flask translate compile
flask run