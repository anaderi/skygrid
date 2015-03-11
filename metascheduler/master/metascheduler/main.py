from .app import *
from .models import *

mongo_host = app.config.get('DB_HOST') or 'localhost'

if app.config['DB_USE_AUTH']:
    connect(
        app.config['DB'],
        username=app.config['DB_USERNAME'],
        password=app.config['DB_PASSWORD'],
        host=mongo_host
    )
else:
    connect(
        app.config['DB'],
        host=mongo_host
    )






# Route all resources
from flask.ext import restful
api = restful.Api(app)

import resources

api.add_resource(resources.StatusResource, '/status')
api.add_resource(resources.JobResource, '/jobs/<string:job_id>')
api.add_resource(resources.JobStatusResource, '/jobs/<string:job_id>/status')
api.add_resource(resources.JobOutputResource, '/jobs/<string:job_id>/output')
api.add_resource(resources.JobInputResource, '/jobs/<string:job_id>/input')


api.add_resource(resources.QueueManagementResource, '/queues')
api.add_resource(resources.QueueResource, '/queues/<string:job_type>')
api.add_resource(resources.QueueInfoResource, '/queues/<string:job_type>/info')