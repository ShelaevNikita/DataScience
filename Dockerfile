FROM ubuntu
RUN apt-get update
RUN apt-get install -y ruby ruby-dev ruby-bundler

FROM python:3.7-slim AS compile-image
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.7-slim AS build-
WORKDIR opencritic
COPY --from=compile-image /opt/venv /opt/venv
COPY OpenCritic.py 
COPY src/dataMining.py
COPY src/plotResults.py
COPY src/dataAnalytics.rb
RUN bundle install .

ENV PATH="/opt/venv/bin:$PATH"
CMD ['python3', '-u', 'OpenCritic.py']

# Commands to run the image:
# sudo docker build -t <image_name> .