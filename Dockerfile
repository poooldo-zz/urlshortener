FROM python:3.4-alpine

MAINTAINER "Nicolas <nicolas@akira.fr>"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "./run.py"]

