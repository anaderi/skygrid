import json
import datetime

from flask import request, jsonify
from flask.ext.restful import reqparse

from ..models import *
from api import MetaschedulerResource, ExistingQueueResource, queue_exists


class QueueManagementResource(MetaschedulerResource):
    def get(self):
        jsoned_queues = []

        queues = Queue.objects()

        for queue in queues:
            jsoned_queues.append(queue.to_dict())

        return {'jobs': jsoned_jobs}

    def put(self):
        queue_dict = json.loads(request.data)

        if len(Queue.objects(job_type=queue_dict['job_type'])) > 0:
            raise Exception('Queue with same job_type already exists')

        queue = Queue(**queue_dict)
        queue.save()

        return {'queue': queue.to_dict()}



class QueueResource(ExistingQueueResource):
    def get(self, job_type):
        n_job = int(request.args.get('njob') or 1) # how many jobs we need to return

        jsoned_jobs = []

        jobs = Job.objects(job_type=job_type, status=JobStatus.Pending)[:n_job]

        for job in jobs:
            job.status = JobStatus.Running
            job.save()

            jsoned_jobs.append(job.to_dict())

        return {'jobs': jsoned_jobs}

    def post(self, job_type):
        job_dict = json.loads(request.data)

        job = Job(job_type=job_type, description=job_dict)
        job.save()

        return {'job': job.to_dict()}

    def delete(self, job_type):
        queue = Queue.objects.get(job_type=job_type)
        queue.delete()



class QueueInfoResource(MetaschedulerResource):
    def get(self, job_type):
        if not queue_exists(job_type):
            return {'exists': False}

        l = len(Job.objects(job_type=job_type, status=JobStatus.Pending))

        return {'length': l, 'exists': True}
