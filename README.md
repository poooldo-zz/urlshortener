# URL shortener setup guide

## Introduction

This is an url shortener using flask and memcached for storage. Follow the below instructions to setup your own instance.
You can give it a try [here](https://s.akira.fr)

## Building from source

To build from source you need to clone the git repo and run docker build:
```
git clone https://github.com/poooldo/urlshortener.git
cd urlshortener
docker build -t urlshortener .
```

## Configuring

### Variables

You need to define two additional variables in you instance/config.py file. These are:

HOST indicating the servername prefix that will be used to send the reply url. Example: http[s]://[www].example.com
SERVERFILE is an absolute file path containing one or several tuples of (server, port), one tuple per line. Example: localhost 11211

### Database

The default database to store the url keys is memcached

```
docker pull memcached
docker run -d -p 11211:11211 -t memcached
```

### Web server

Change variables accordingly.

```
server {

    listen x.x.x.x;
    server_name example.com;

    access_log /var/log/nginx/example.com_access.log;
    error_log /var/log/nginx/example.com_error.log;

    location / {
        proxy_redirect      off;
        proxy_buffering     off;
        proxy_set_header    Host            $host;
        proxy_set_header    X-Real-IP       $remote_addr;
        proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto    $scheme;

        proxy_pass http://127.0.0.1:5000;
}
```

## Running

```
docker run --network=host -d -t urlshortener
```

## Logging

All logs print out in stdout/stderr and are available via the docker logs command:
```
docker logs <CONTAINER_ID>
```
