import flask
from flask import Flask
from flask.ext.cors import CORS

app = Flask(__name__)
app.config.from_envvar('METASCHEDULER_CONFIG')
cors = CORS(app)
