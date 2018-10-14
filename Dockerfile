FROM continuumio/miniconda3:latest

# set build-time environment variables
ENV WS=/home/lws_user/Life_Web_Service
ENV FLASK_APP run.py

# create service account
RUN adduser --disabled-password --gecos "" lws_user

# declare workspace
RUN mkdir -p $WS
WORKDIR $WS

# create conda environment
COPY envs envs
RUN conda env create -f envs/environment.yaml

# install application
COPY lws lws
COPY migrations migrations
COPY run.py launch_dk.sh ./
RUN chmod +x launch_dk.sh

# launch application
RUN chown -R lws_user:lws_user ./
USER lws_user
EXPOSE 5000
ENTRYPOINT ["./launch_dk.sh"]