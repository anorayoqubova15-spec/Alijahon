FROM python:3.12-alpine
WORKDIR /var/www/alijahon

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY . .
