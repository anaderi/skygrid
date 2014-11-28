import flask
from flask import Flask

app = Flask(__name__)
app.config.from_envvar('METASCHEDULER_CONFIG')
