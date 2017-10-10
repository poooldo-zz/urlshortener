from app import app
#app.run(debug=True)
from werkzeug.contrib.fixers import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app)
app.run(debug=False, threaded=True)
