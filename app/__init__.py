from flask import Flask

app = Flask(__name__, instance_relative_config=True)
#app = Flask(__name__)
app.config.from_object('config')
app.config.from_pyfile('config.py')
from app import views
