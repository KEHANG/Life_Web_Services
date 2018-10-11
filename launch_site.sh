source activate lws_env
gunicorn -b localhost:8000 -w 4 run:lws_app