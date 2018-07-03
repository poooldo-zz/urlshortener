from app import app
from app import database
from flask import render_template, redirect, request
from flask import jsonify
import random
import re
import json

####################################
##### App parameters loading #######
####################################

db_class = getattr(database, app.config['DB_DRIVER'])
db_host = app.config['DB_HOST']

if 'DB_USERNAME' in app.config:
    db_username = app.config['DB_USERNAME']
else:
    db_username = None 

if 'DB_PASSWORD' in app.config:
    db_password = app.config['DB_PASSWORD']
else:
    db_password = None 

if 'DB_KEYEXP' in app.config:
    key_expiration = app.config['DB_KEYEXP'] 
else:
    key_expiration = 36000

# loading the database backend
db = db_class(host=db_host, username=db_username, password=db_password, key_expiration=key_expiration)

# the key base to use for generating a shorten url
ALPHA_BASE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# key length to generate a shorten url
KEY_LEN= int(app.config['KEYLEN'])
# the application domain
WEB_HOST = app.config['WEB_HOST']
REDIRECT_CODE = 302

####################################
####### HTTP error handlers ########
####################################

@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html', error=error, host=WEB_HOST), 400

@app.errorhandler(404)
def page_not_found():
    return render_template('404.html', host=WEB_HOST), 404

####################################
############ Frontend ##############
####################################

@app.route('/')
def index():
    """
    The application homepage 
    @params:
    @returns:
    """
    return render_template('index.html'), 200 

@app.route('/', methods=['POST'])
def post_index():
    """
    Handle user form in the homepage to
    shorten an url
    @params:
        url: the url to shorten
    @returns:
        the shorten url and an error page
        with the status on failure
    """
    url = request.form['url']
    result = api_shorten()
    json_data = json.loads(result.data.decode('utf-8'))
    if json_data['status'] == 'ok':
        return "{}".format(json_data['url'])
    return bad_request(json_data['status'])

@app.route('/admin/stats')
def admin():
    """
    Get the statistics of shorten url
    in the database
    @params:
    @returns:
        the page containing the statistics
    """
    pass

####################################
############ Backend ###############
####################################

@app.route('/<path:path>')
def api_catch_all(path):
    """
    Redirect from shorten url to the standard form
    @params:
        the shorten code in the url
    @returns:
        redirect to the url if success
        404 page (not found) if not match
    """
    value = db.get_value(path) 
    if value is not None:
        return redirect(value, REDIRECT_CODE)
    else:
        return page_not_found()

@app.route('/api/shorten')
def api_shorten():
    """
    Shorten an url given in parameters
    @params:
        url: contains the url to shorten
    @returns:
        Flask Response containing the status
        and the shorten url if success
    """
    url = request.values.get('url')
    if not url:
        return jsonify({'status': 'url missing - expected : http[s]://domain.gtld/[args]'})
    url_is_valid = re.fullmatch('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
    if url_is_valid is None:
        return jsonify({'status': 'not a valid url - expected : http[s]://domain.gtld/[args]'})
    ukey = ""
    value = ""
    while value is not None:
        while len(ukey) < KEY_LEN:
            ukey = "{}{}".format(ukey, random.choice(ALPHA_BASE))
        value = db.get_value(ukey)
    db.set_value(ukey, url)
    return jsonify({'status': 'ok', 'url': '{}/{}'.format(WEB_HOST, ukey)})

@app.route('/api/list')
def api_shorten_list():
    """

    """
    return "list"

@app.route('/api/stat')
def api_shorten_stat():
    """
    Get statistics for a shorten code
    @params:
        key: contains the shorten code
    @returns:
        Flask Response containing the status
        and the statistics if success
    """
    short_name = request.args.get('key')
    if not short_name:
        return jsonify({'status': 'short code missing'})
    hit_count = db.get_stat(short_name)
    if hit_count is not None:
        return jsonify({'status': 'ok', 'url': '{}'.format(short_name), 'hit_count': '{}'.format(hit_count)})
    return jsonify({'status': 'short url not found', 'url': '{}'.format(short_name)})
