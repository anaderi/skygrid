import flask
from flask import Flask
from flask.ext.cors import CORS

from mongoengine import connect
from gevent import monkey

from libscheduler import Metascheduler


app = Flask(__name__)
app.config.from_envvar('SKYGRID_CONFIG')
cors = CORS(app)


# Configure DB

mongo_host = app.config.get('MONGO_DB_HOST') or 'localhost'

if app.config['DB_USE_AUTH']:
    connect(
        app.config['MONGO_DB'],
        username=app.config['MONGO_DB_USERNAME'],
        password=app.config['MONGO_DB_PASSWORD'],
        host=mongo_host
    )
else:
    connect(
        app.config['MONGO_DB'],
        host=mongo_host
    )


# Configure metascheduler
app.metascheduler = Metascheduler(app.config['METASCHEDULER_URL'])


# Configure blueprints
import datasets
import classifiers
import montecarlo


app.register_blueprint(datasets.blueprint)
app.register_blueprint(classifiers.blueprint)
app.register_blueprint(montecarlo.blueprint)

monkey.patch_all() # if not started by gunicorn
