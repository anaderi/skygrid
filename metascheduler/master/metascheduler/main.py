from .app import *
from .models import *


# REST API things
from flask.ext import restful

from .resources import (
    JobResource,
    QueueManagementResource,
    QueueResource,
    QueueInfoResource
)


api = restful.Api(app)
api.add_resource(JobResource, '/jobs/<string:job_id>')

api.add_resource(QueueManagementResource, '/queues')
api.add_resource(QueueResource, '/queues/<string:job_type>')
api.add_resource(QueueInfoResource, '/queues/<string:job_type>/info')
