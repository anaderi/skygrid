import flask
from flask import Flask

app = Flask(__name__)
app.config.from_envvar('SHIP_FRONTEND_CONFIG')


# Connect to database
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
