import urlshortener.application
import json
import os
import unittest

class AppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass 

    @classmethod
    def tearDownClass(cls):
        pass 
    
    def setUp(self):
        pass
        self.app = urlshortener.application.app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_homepage(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_redirect(self):
        response = self.app.get('/test')
        self.assertEqual(response.status_code, 301)
        
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

    def test_api_shorten_stat(self):
        pass

    def test_api_admin(self):
        pass

if __name__ == "__main__":
    unittest.main()
