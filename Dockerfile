FROM python:3.4-jessie

MAINTAINER "Nicolas <nicolas@akira.fr>"

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y lsb-release && \
    curl -O http://packages.couchbase.com/releases/couchbase-release/couchbase-release-1.0-4-amd64.deb && \
    dpkg -i couchbase-release-1.0-4-amd64.deb

RUN apt-get update && apt-get install -y \
    gcc build-essential libcouchbase-dev
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "./run.py"]

