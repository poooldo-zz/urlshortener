class Memcache(object):
    """
    This class is an interface to a memcache storage backend
    it implements needed methods to store and fetch for an url 
    shortener.
    """

    from pymemcache.client.hash import HashClient
    
    def __init__(self, host, key_expiration, username=None, password=None):
        self.client = HashClient(
            servers=host,
            connect_timeout=True,
            timeout=True,
            use_pooling=True,
            max_pool_size=100
            )
        self.key_expiration = key_expiration

    def set_value(self, key, value):
        return self.client.set(key, value.encode('utf-8'), self.key_expiration)

    def get_value(self, key):
        res = None
        res = self.client.get(key)
        if res is not None:
            return res.decode('utf-8')
        return None

class Couchbase(object):
    """
    This class is an interface to a couchbase storage backend
    it implements the methods to store and fetch for an url shortener
    with statistics on hits.
    """
    import couchbase
    from couchbase.admin import Admin
    from couchbase.bucket import Bucket
    from couchbase.cluster import Cluster
    from couchbase.cluster import PasswordAuthenticator
    import json

    def __init__(self, host, username, password, key_expiration):
        cluster = self.Cluster('couchbase://{}'.format(host))
        authenticator = self.PasswordAuthenticator(username, password)
        cluster.authenticate(authenticator)
        self.bucket = cluster.open_bucket('shortener')
        self.key_expiration = key_expiration

    #TODO reconnect after losing connection
    def reconnect(self):
        pass

    def set_value(self, key, value):
        try:
            self.bucket.insert(key, {'url': value, 'hit_count': 0}, 
                               ttl=self.key_expiration,
                               format=self.couchbase.FMT_JSON)
        except self.couchbase.exceptions.KeyExistsError:
            return False
        return True

    def get_value(self, key):
        try:
            value = self.bucket.get(key).value
        except self.couchbase.exceptions.NotFoundError:
            return None
        value['hit_count'] += 1
        self.bucket.replace(key, value)
        return value['url']

    def get_stat(self, key):
        try:
            value = self.bucket.get(key).value
        except self.couchbase.exceptions.NotFoundError:
            return None
        return value['hit_count']

    def get_urls(self):
        pass

if __name__ == '__main__':

    cb = Couchbase(host='51.38.45.89', username='admin', password='tzgz61fen', key_expiration=60)
    cb.set_value('test', 'http://slashdot.org')
    e = cb.get_value('test')
    print(e)
