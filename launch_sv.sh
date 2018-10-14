source activate lws_env
flask db upgrade
flask translate compile
gunicorn -b localhost:8000 -w 4 run:lws_app