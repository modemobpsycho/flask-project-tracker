FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN apt-get update && apt-get install -y postgresql-client

CMD bash -c 'while !</dev/tcp/localhost/5432; do sleep 1; done; flask run'
