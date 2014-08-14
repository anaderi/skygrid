from flask import Flask
from ..generic.models import *

app = Flask(__name__)

app.config.from_envvar('SHIP_FRONTEND_CONFIG')

connect(app.config['DB']) # connect to MongoDB

from views import *
