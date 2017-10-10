from app import app
from flask import render_template, redirect, request
from app import database
import random
import re

srvs = []
with open(app.config['DB_SERVERS']) as file_servers:
    for line in file_servers:
        server_name, server_port = line.split()
        srvs.append((server_name, int(server_port)))
db = database.Database(servers=srvs)

if app.config['ALPHABASE'] == 'auto':
    ALPHA_BASE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
else:
    ALPHA_BASE = app.config['ALPHABASE']

KEY_LEN= int(app.config['KEYLEN'])
HOST = app.config['HOST']
REDIRECT_CODE = app.config['REDIRECT_CODE']

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html'), 200 

@app.route('/<path:path>')
def catch_all(path):
    value = db.get_value(path) 
    if value is not None:
        return redirect(value, REDIRECT_CODE)
    else:
        return render_template('404.html'), 404

@app.route('/api/shorten')
def shorten():
    url = request.args.get('url')
    url_is_valid = re.fullmatch('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
    if url_is_valid is None:
        return render_template('400.html'), 400
    ukey = ""
    value = ""
    while value is not None:
        while len(ukey) < KEY_LEN:
            ukey = "{}{}".format(ukey, random.choice(ALPHA_BASE))
        value = db.get_value(ukey)
    db.set_value(ukey, url)
    return "{}/{}".format(HOST, ukey)
