from urllib.parse import urlparse

from urlshortener import database
from flask import render_template, redirect, request, Response
from flask import jsonify
from functools import wraps
from passlib.hash import argon2
import json
import random
import re

from urlshortener.application import WEB_HOST, admin_hash, db, REDIRECT_CODE, MAX_URL_SIZE, KEY_LEN, ALPHA_BASE, app

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
######## Basic Auth mecanism #######
####################################

def check_auth(username, password):
    """
    This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and argon2.verify(password, admin_hash)


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


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
        return render_template('index.html', url='https://{}'.format(json_data['url'])), 200
    return bad_request(json_data['status'])


@app.route('/admin/stats')
@requires_auth
def admin():
    """
    Get the statistics of shorten url
    in the database
    @params:
    @returns:
        the page containing the statistics
    """
    results_list = []
    results = db.get_all()
    for result in results:
        results_list.append(result)
    return render_template('admin.html', results=results_list), 200


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
    if len(url) > MAX_URL_SIZE:
        return jsonify({'status': 'url too long - must be under 2000 chars'})
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


@app.route('/api/admin')
@requires_auth
def api_admin():
    """
    Get all id, url, hit_count in
    the database
    @params:
    @returns:
        a json object containing all
        database information
    """
    results_list = []
    results = db.get_all()
    for result in results:
        results_list.append(result)
    return jsonify(results_list)
