from flask import Flask
from flask.ext import restful

from ..generic.models import *

app = Flask(__name__)
api = restful.Api(app)

app.config.from_envvar('SHIP_FRONTEND_CONFIG')

connect(app.config['DB']) # connect to MongoDB

from views import *


from resources import JobResource

api.add_resource(JobResource, '/jobs/<string:job_id>')
