# URL shortener setup guide

## Introduction

This is an url shortener using Flask and Couchbase or Memcached for storage. Follow the below instructions to setup your own instance.
You can give it a try [here](https://s.akira.fr)

## Technical choices

### Database

The first release was developed using a non-persistent storage (Memcached). The current release needed a persistent storage system.
As url minifier basically means storing key/value elements, we use Couchbase, which features persisent storage, key/value store and 
scalability with data replication, clustering and data partitioning.

Configuring a high-availability cluster using Couchbase is out of the scope of this document, but this information can be found 
on the official website.

### Web service

Flask serve the API and the webpage. It is a lightweight framework to develop API. It uses Jinja2 templating system
in order to have smartly generated html pages. Moreover, Flask can be easily scalable, is well-documented and widely use.

We suggest to put Nginx as a proxy to Flask in order to handle secure connection to the service (https) as well as letsencrypt to 
manage the ssl certificate.

### Data structure

As we use a key/value storage system, the key is the shorten code of the url and the value is a json object containing the url
we want to shorten and the hit count to keep track of requests to the short url. As in the orginal release with memcache, every
entries in the database can have a ttl. For this, we use the ttl feature in Couchbase entries.

### Shorten url generation algorithm

The shorten code generation algorithm use a set of characters as space entropy, which can be configured. It also uses a configurable 
code size to increase or decrease the number of urls that can be generated. The ttl in every entry also helps cleaning the database 
to have enough space during time. To generate a shorten code, we just random choosing a character in the set until the configured
size is reached.

The default character-set is '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.

With a 8-characters length key, the default character-set, the number of possible short codes is 218340105584896 (62 ^ 8). At a rate
of 1000 requests/s, it would takes 2 527 084 days to generate every code permutations which is fair.

There is many ways to deal with the code generation, for example generating a hash from the url we want to shorten. The
technique used here is pretty fast, allows different code for the same orginal url, and a shorten url can't be predicted
from the original one.

### Basic authentication

Basic authentication is implemented using a Flask Basic Auth template. The password checking function use the Argon2 password hash 
method. This method is considered secure, Argon2 was designed to resist against GPU and side-channels attacks.

### Known limitations

* The shorten code generator can suffer collisions while generating, this is handle by generating a code again until it does not exist.
* There is no support for registered users. 
* The hit count could be handle by Couchbase Counter type. Could be in a future release.
* The memcache driver does not support the hit count for now.

## Building from source

To build from source you need to clone the git repo and run docker build:
```
git clone https://github.com/poooldo/urlshortener.git
cd urlshortener
docker build -t urlshortener .
```

## Configuring

### Variables

* **DB_DRIVER** the database driver to use. Couchbase or Memcache available. Couchbase should be privileged. 
* **DB_HOST** the domain name or ip address to the database
* **DB_USERNAME** the username to connect to the database(default: None)
* **DB_PASSWORD** the corresponding password (default: None)
* **DB_KEYEXP** key expiration time in seconds (default: 36000 seconds)
* **KEYLEN** key length of the shorten code (default: 8)
* **WEB_HOST** domain name of the service

### Database

Spawning a Couchbase instance using Docker is pretty straightforward. You need to create a bucket called shortener.
Once it is done, create an index on the bucket using the query:

```
CREATE PRIMARY INDEX ON shortener;
```

Now the database is ready! Do not forget to setup the appropriate firewall rules.

### Web server

Use Nginx as proxy mainly to handle secure connections.
Change variables accordingly.

```
server {

    listen x.x.x.x;
    server_name example.com;

    access_log /var/log/nginx/example.com_access.log;
    error_log /var/log/nginx/example.com_error.log;
    
    ssl on;
    ssl_certificate /path/to/certificate;
    ssl_certificate_key /path/to/private/key; 
    ssl_prefer_server_ciphers On;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:!aNULL:!eNULL:!DES:!3DES:!MD5:!PSK:!EXPORT:!DSS:-LOW:-SSLv2:-EXP;
    ssl_session_timeout 10m;
    ssl_session_cache shared:ssl_session_cache:10m;
    ssl_dhparam /path/to/dh/parameter;

    location / {
        proxy_redirect      off;
        proxy_buffering     off;
        proxy_set_header    Host                $host;
        proxy_set_header    X-Real-IP           $remote_addr;
        proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;
        proxy_set_header    X-Forwarded-Proto   $scheme;
        proxy_set_header    Authorization       $http_authorization;
        proxy_pass_header   Authorization;

        proxy_pass http://127.0.0.1:5000;
}
```

## Administrator password

Use passlib (pip install passlib) and python to generate the password hash of the application and store it into a file called .password.

Example:

```
>>> from passlib.hash import argon2
>>> h = argon2.hash("password")
>>> h
'$argon2i$v=19$m=512,t=2,p=2$aI2R0hpDyLm3ltLa+1/rvQ$LqPKjd6n8yniKtAithoR7A'
```

## Running

```
docker run -p 5000:5000 -d -t urlshortener
```

## Logging

All logs print out in stdout/stderr and are available via the docker logs command:
```
docker logs <CONTAINER_ID>
```
