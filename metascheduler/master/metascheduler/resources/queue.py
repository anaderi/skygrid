import json
import datetime

import pymongo
from flask import request, jsonify
from flask.ext.restful import reqparse

from ..models import *
from ..rabbit import (
    rmq_push_to_queue,
    rmq_pull_from_queue,
    rmq_delete_queue,
    rmq_queue_length
)

from api import MetaschedulerResource, ExistingQueueResource, queue_exists


class QueueManagementResource(MetaschedulerResource):
    def get(self):
        jsoned_queues = []

        queues = Queue.objects()

        for queue in queues:
            jsoned_queues.append(queue.to_dict())

        return {'queues': jsoned_queues}

    def put(self):
        queue_dict = json.loads(request.data)

        if len(Queue.objects(job_type=queue_dict['job_type'])) > 0:
            raise Exception('Queue with same job_type already exists')

        queue = Queue(**queue_dict)
        queue.save()

        return {'queue': queue.to_dict()}



class QueueResource(ExistingQueueResource):
    def get(self, job_type):
        return {'job': rmq_pull_from_queue(job_type) }

    def post(self, job_type):
        job_dict = json.loads(request.data)

        job = Job(job_type=job_type, descriptor=job_dict)
        job.save()

        rmq_push_to_queue(job_type, json.dumps(job.to_dict()))

        return {'job': job.to_dict()}

    def delete(self, job_type):
        queue = Queue.objects.get(job_type=job_type)
        queue.delete()
        rmq_delete_queue(job_type)




class QueueInfoResource(MetaschedulerResource):
    def get(self, job_type):
        if not queue_exists(job_type):
            return {'exists': False}

        return {'length': rmq_queue_length(job_type), 'exists': True}
