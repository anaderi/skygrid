from flask import Flask
from flask.ext import restful

from mongoengine import connect
from ..generic.models import *

app = Flask(__name__)
api = restful.Api(app)

app.config.from_envvar('SHIP_FRONTEND_CONFIG')

if app.config['DB_USE_AUTH']:
    connect(app.config['DB'], username=app.config['DB_USERNAME'], password=app.config['DB_PASSWORD'])
else:
    connect(app.config['DB'])

from views import *


from resources import *

api.add_resource(JobResource, '/job/<string:job_id>')

api.add_resource(QueueManagementResource, '/queues')
api.add_resource(QueueResource, '/queues/<string:job_type>')
api.add_resource(QueueInfoResource, '/queues/<string:job_type>/info')
