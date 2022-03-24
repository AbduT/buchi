FROM python:3.8
WORKDIR /app

ADD requirements.txt /app/requirements.txt

RUN pip install --upgrade -r requirements.txt

EXPOSE 8080

ADD ./app/ /app/

ADD config.conf /app/config.conf

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]