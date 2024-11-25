FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /django

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
