class Memcache(object):
    """
    This class is an interface to a memcache storage backend
    it implements needed methods to store and fetch for an url 
    shortener.
    """

    from pymemcache.client.hash import HashClient
    
    def __init__(self, host, key_expiration, username=None, password=None):
        """
        Instanciate a memcache storage backend object
        @params:
            host: the server to connect to
            key_expiration: key expiration in seconds
            username: not use
            password: not use
        @returns:
        """
        self.client = HashClient(
            servers='{} 11211'.format(host),
            connect_timeout=True,
            timeout=True,
            use_pooling=True,
            max_pool_size=100
            )
        self.key_expiration = key_expiration

    def set_value(self, key, value):
        """
        Set a new record in the datavase for a short code
        @params:
            key: the short code to insert
            value: the long url corresponding
        @returns:
            True or False if succeeded or not
        """
        return self.client.set(key, value.encode('utf-8'), self.key_expiration)

    def get_value(self, key):
        """
        Get a long url from the shorten form
        @params:
            key: the short form to lookup
        @returns:
            a long url if found, None otherwise
        """
        res = None
        res = self.client.get(key)
        if res is not None:
            return res.decode('utf-8')
        return None
    
    def get_stat(self, key):
        pass

    def get_all(self):
        pass

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
    from couchbase import LOCKMODE_WAIT
    from couchbase.cluster import PasswordAuthenticator
    import json
    import threading

    def __init__(self, host, username, password, key_expiration):
        """
        Instanciate a couchbase storage backend object
        @params:
            host: the server to connect to
            key_expiration: key expiration in seconds
            username: the user to connect to the database
            password: the related password
        @returns:
        """
        cluster = self.Cluster('couchbase://{}'.format(host))
        authenticator = self.PasswordAuthenticator(username, password)
        cluster.authenticate(authenticator)
        self.bucket = cluster.open_bucket('shortener', lockmode=self.LOCKMODE_WAIT)
        self.key_expiration = key_expiration
        self.lock = self.threading.Lock()

    #TODO reconnect after losing connection
    def reconnect(self):
        pass

    def set_value(self, key, value):
        """
        Set a new record in the datavase for a short code
        @params:
            key: the short code to insert
            value: the long url corresponding
        @returns:
            True or False if succeeded or not
        """
        try:
            self.bucket.insert(key, {'url': value, 'hit_count': 0}, 
                               ttl=self.key_expiration,
                               format=self.couchbase.FMT_JSON)
        except self.couchbase.exceptions.KeyExistsError:
            return False
        return True

    def get_value(self, key):
        """
        Get a long url from the shorten form
        @params:
            key: the short code to lookup
        @returns:
            a long url if found, None otherwise
        """
        self.lock.acquire()
        try:
            value = self.bucket.get(key).value
        except self.couchbase.exceptions.NotFoundError:
            return None
        value['hit_count'] += 1
        self.bucket.replace(key, value)
        self.lock.release()
        return value['url']

    def get_stat(self, key):
        """
        Get the hit counter for a shorten url
        @params:
            key: the shorten code to lookup
        @returns:
            the hit count value, None otherwise
        """
        try:
            value = self.bucket.get(key).value
        except self.couchbase.exceptions.NotFoundError:
            return None
        return value['hit_count']

    def get_all(self):
        """
        Get all urls, shorten code and statistics from
        the database
        @params:
        @returns:
            a json containing all the data, None otherwise
        """
        rows = self.bucket.n1ql_query('SELECT META().id, url, hit_count FROM shortener')
        return rows

if __name__ == '__main__':

    cb = Couchbase(host='51.38.45.89', username='admin', password='tzgz61fen', key_expiration=60)
    cb.set_value('test', 'http://slashdot.org')
    e = cb.get_value('test')
    print(e)
    rows = cb.get_all()
    for r in rows:
        print(r)
