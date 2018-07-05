from urlshortener.database import Couchbase
import time

now = str(int(time.time()))
url = 'http://google.com'
host = '51.38.45.89'
username = 'admin'
password = 'tzgz61fen'
low_exp = 1
high_exp = 360000

def test_set_value():
    db = Couchbase(host, username, password, high_exp)
    assert db.set_value(now, url)

def test_get_value():
    db = Couchbase(host, username, password, high_exp)
    assert db.get_value(now) == url

def test_get_stat():
    db = Couchbase(host, username, password, high_exp)
    assert db.get_stat(now) == 1

def test_key_expiration():
    db = Couchbase(host, username, password, low_exp)
    key = str(int(time.time()) + 1)
    db.set_value(key, url)
    time.sleep(2)
    assert db.get_value(key) == None

def test_get_all():
    db = Couchbase(host, username, password, high_exp)
    results = db.get_all()
    key = str(int(time.time()) + 2)
    db.set_value(key, url)
    for result in results:
        if result['id'] == key:
            assert result['url'] == url
            assert result['hit_count'] == 0
        elif result['id'] == now:
            assert result['url'] == url
            assert result['hit_count'] == 1
    
def test_get_stat_key_not_exists():
    db = Couchbase(host, username, password, high_exp)
    assert db.get_stat('a') == None
   
def test_set_value_already_exists():
    db = Couchbase(host, username, password, high_exp)
    assert db.set_value(now, url) == False
