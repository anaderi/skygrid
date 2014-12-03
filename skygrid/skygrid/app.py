import flask
from flask import Flask
from flask.ext.cors import CORS

from mongoengine import connect

from libscheduler import Metascheduler


app = Flask(__name__)
app.config.from_envvar('SKYGRID_CONFIG')
cors = CORS(app)

# FIXME: handle https scenario
app.config['FULL_URL'] = "http://{}:{}/".format(app.config['HOSTNAME'], app.config['PORT'])

# Configure DB
if app.config['DB_USE_AUTH']:
    connect(app.config['MONGO_DB'], username=app.config['MONGO_DB_USERNAME'], password=app.config['MONGO_DB_PASSWORD'])
else:
    connect(app.config['MONGO_DB'])


# Configure metascheduler
app.metascheduler = Metascheduler(app.config['METASCHEDULER_URL'])


# Configure blueprints
from datasets import blueprint as datasets_blueprint
from classifiers import blueprint as classifiers_blueprint

app.register_blueprint(datasets_blueprint)
app.register_blueprint(classifiers_blueprint)

