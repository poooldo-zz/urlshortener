from pymemcache.client.hash import HashClient


class Database(object):
    
    def __init__(self, servers, key_expiration):
        self.client = HashClient(
            servers=servers,
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
