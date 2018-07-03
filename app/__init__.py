from flask import Flask

#app = Flask(__name__, instance_relative_config=True)
app = Flask(__name__, instance_path='/root/dev/ursho/src')
print(app.instance_path)
#app.config.from_object('config')
app.config.from_pyfile('config.py')
from app import views
