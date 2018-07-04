from app import app
#app.run(debug=True)
from werkzeug.contrib.fixers import ProxyFix
#import logging
#import sys
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app.wsgi_app = ProxyFix(app.wsgi_app)
app.run(debug=False, threaded=True)
