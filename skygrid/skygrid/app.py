import flask
from flask import Flask

from mongoengine import connect

from libscheduler import Metascheduler


app = Flask(__name__)
app.config.from_envvar('SKYGRID_FRONTEND_CONFIG')

# Configure DB
if app.config['DB_USE_AUTH']:
    connect(app.config['MONGO_DB'], username=app.config['MONGO_DB_USERNAME'], password=app.config['MONGO_DB_PASSWORD'])
else:
    connect(app.config['MONGO_DB'])

# Configure metascheduler
app.metascheduler = Metascheduler(app.config['METASCHEDULER_URL'])

# Configure blueprints
from datasets import blueprint as datasets_blueprint

app.register_blueprint(datasets_blueprint)

