from flask import Flask
from flask.ext import restful

from mongoengine import connect

app = Flask(__name__)
api = restful.Api(app)

app.config.from_envvar('SHIP_FRONTEND_CONFIG')

if app.config['DB_USE_AUTH']:
    connect(app.config['DB'], username=app.config['DB_USERNAME'], password=app.config['DB_PASSWORD'])
else:
    connect(app.config['DB'])

from views import *


from resources import JobResource, QueueLengthResource, QueueResource

api.add_resource(JobResource, '/job/<string:job_id>')
api.add_resource(QueueResource, '/queues/<string:job_type>')
api.add_resource(QueueLengthResource, '/queues/<string:job_type>/length')
