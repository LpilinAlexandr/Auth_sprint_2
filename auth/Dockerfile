FROM python:3.9.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m pip install --upgrade pip

WORKDIR auth

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

ENV PYTHONPATH "${PYTHONPATH}:/auth"
ENV FLASK_APP=app:main

EXPOSE 5000