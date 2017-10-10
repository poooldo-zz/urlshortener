from pymemcache.client.hash import HashClient


class Database(object):
    
    def __init__(self, servers):
        self.client = HashClient(
            servers=servers,
            connect_timeout=True,
            timeout=True,
            use_pooling=True,
            max_pool_size=100
            )

    def set_value(self, key, value):
        return self.client.set(key, value.encode('utf-8'), 3600)

    def get_value(self, key):
        res = None
        res = self.client.get(key)
        if res is not None:
            return res.decode('utf-8')
        return None
