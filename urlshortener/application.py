from flask import Flask
from urlshortener import config, database

app = Flask(__name__)
app.config.from_object(config)


####################################
##### App parameters loading #######
####################################

with open(".password") as hashfile:
    admin_hash = hashfile.readline()[:-1]

db_class = getattr(database, app.config['DB_DRIVER'])
db_host = app.config.get('DB_HOST', '127.0.0.1')

# todo
db_username = app.config.get('DB_USERNAME', None)
db_password = app.config.get('DB_PASSWORD', None)
key_expiration = app.config.get('DB_KEYEXP', 36000)

KEY_LEN = app.config.get('KEYLEN', 8)

# loading the database backend we selected
db = db_class(host=db_host, username=db_username, password=db_password, key_expiration=key_expiration)

# the key base to use for generating a shorten url
ALPHA_BASE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# the application domain
WEB_HOST = app.config['WEB_HOST']
REDIRECT_CODE = 301
MAX_URL_SIZE = 2000



from urlshortener import views
