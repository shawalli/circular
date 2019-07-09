FROM python:3.7-slim-stretch

COPY . /app

WORKDIR /app

RUN pip install pipenv

RUN pipenv install --verbose

RUN chmod +x circular.py

# RUN pipenv run ./circular.py -vvv --out /appdata/download_c.png /appdata/download.png
