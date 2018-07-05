import urlshortener.application
import json
import os
import unittest
from base64 import b64encode

class WebTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass 

    @classmethod
    def tearDownClass(cls):
        pass 
    
    def setUp(self):
        self.app = urlshortener.application.app.test_client()
        self.app.testing = True
        if urlshortener.application.db.get_value("test") is None:
            urlshortener.application.db.set_value("test", "https://www.fasterize.com/")

    def tearDown(self):
        pass

    def test_homepage(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_redirect(self):
        response = self.app.get('/test')
        self.assertEqual(response.status_code, 301)
    
    def test_admin(self):
        cred = b64encode(b"admin:secret").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' % cred }
        response = self.app.get('/admin/stats', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_restricted_access(self):
        response = self.app.get('/admin/stats')
        self.assertEqual(response.status_code, 401)

    def test_api_shorten(self):
        response = self.app.get('/api/shorten?url=https://www.fasterize.com/')
        json_data = json.loads(response.data.decode('utf-8'))
        assert json_data['status'] == 'ok'

    def test_api_shorten_bad_url(self):
        response = self.app.get('/api/shorten?url=aaaaaaaaa')
        json_data = json.loads(response.data.decode('utf-8'))
        assert json_data['status'] == 'not a valid url - expected : http[s]://domain.gtld/[args]'
        
    def test_api_shorten_empty_url(self):
        response = self.app.get('/api/shorten?url=')
        json_data = json.loads(response.data.decode('utf-8'))
        assert json_data['status'] == 'url missing - expected : http[s]://domain.gtld/[args]'

    def test_api_shorten_too_long_url(self):
        url = "http://google.com/{}".format('a' * 2000)
        response = self.app.get('/api/shorten?url={}'.format(url))
        json_data = json.loads(response.data.decode('utf-8'))
        assert json_data['status'] == 'url too long - must be under 2000 chars'
    
    def test_api_shorten_invalid_url(self):
        response = self.app.get('/api/shorten?url=ddd')
        json_data = json.loads(response.data.decode('utf-8'))
        assert json_data['status'] == 'not a valid url - expected : http[s]://domain.gtld/[args]'

    def test_api_shorten_stat_missing(self):
        response = self.app.get('/api/stat')
        json_data = json.loads(response.data.decode('utf-8'))
        assert json_data['status'] == 'short code missing'
       
    def test_api_shorten_stat_not_found(self):
        response = self.app.get('/api/stat?key=a')
        json_data = json.loads(response.data.decode('utf-8'))
        assert json_data['status'] == 'short url not found'

    def test_api_shorten_stat_ok(self):
        response = self.app.get('/api/stat?key=test')
        json_data = json.loads(response.data.decode('utf-8'))
        assert json_data['status'] == 'ok'
    
    def test_api_admin(self):
        cred = b64encode(b"admin:secret").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' % cred }
        response = self.app.get('/api/admin', headers=headers)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
