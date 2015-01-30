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



from flask.ext import restful

from .resources import (
    StatusResource,
    JobResource,
    QueueManagementResource,
    QueueResource,
    QueueInfoResource,
)


api = restful.Api(app)
api.add_resource(StatusResource, '/status')
api.add_resource(JobResource, '/jobs/<string:job_id>')

api.add_resource(QueueManagementResource, '/queues')
api.add_resource(QueueResource, '/queues/<string:job_type>')
api.add_resource(QueueInfoResource, '/queues/<string:job_type>/info')