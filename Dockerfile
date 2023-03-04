FROM ubuntu:22.04
MAINTAINER Danil Shevelev 'danil.shevelev.2004@mail.ru'
RUN apt-get update -qy
# libpq-dev - обязательно для работы библиотеки `psycopg2`.
RUN apt-get install -qy python3.11 python3-pip python3.11-dev libpq-dev
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "app.py"]