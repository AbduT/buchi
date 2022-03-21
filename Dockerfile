FROM python:3.8
WORKDIR /app

ADD requirements.txt /app/requirements.txt

RUN pip install --upgrade -r requirements.txt

EXPOSE 8000
EXPOSE 27017

COPY ./app/ /app/

RUN cd /app

RUN uvicorn app:app --reload --host 0.0.0.0 --port 8000