import json
import datetime

from flask import request, jsonify
from flask.ext.restful import reqparse

from ...generic.models import Job, Queue
from ...generic.api import MetaschedulerResource

class QueueManagementResource(MetaschedulerResource):
    def get(self):
        jsoned_queues = []

        queues = Queue.objects()

        for queue in queues:
            jsoned_queues.append(queue.to_dict())

        return {'jobs': jsoned_jobs}

    def put(self):
        print request.data
        queue_dict = json.loads(request.data)

        if len(Queue.objects(job_type=queue_dict['job_type'])) > 0:
            raise Exception('Queue with same job_type already exists')

        queue = Queue(**queue_dict)
        queue.save()

        return {'queue': queue.to_dict()}



class QueueResource(MetaschedulerResource):
    def get(self, job_type):
        n_job = int(request.args.get('njob') or 1) # how many jobs we need to return

        jsoned_jobs = []

        jobs = Job.objects(job_type=job_type)[:n_job]

        for job in jobs:
            jsoned_jobs.append(job.to_dict())
            job.delete()

        return {'jobs': jsoned_jobs}

    def post(self, job_type):
        job_dict = json.loads(request.data)

        job = Job(job_type=job_type, description=job_dict)
        job.save()

        return {'job': job.to_dict()}


class QueueLengthResource(MetaschedulerResource):
    def get(self, job_type):
        l = len(Job.objects(job_type=job_type))

        return {'length': l}
