import json
import datetime

import pymongo
from flask import request, jsonify
from flask.ext.restful import reqparse

from ..models import *

from api import MetaschedulerResource, ExistingQueueResource, queue_exists

def queue_length(queue_name):
    return len(Job.objects(job_type=queue_name, status=JobStatus.pending))


class QueueManagementResource(MetaschedulerResource):
    def get(self):
        jsoned_queues = []

        queues = Queue.objects().all()

        for queue in queues:
            q_dict = queue.to_dict()
            q_dict['length'] = queue_length(queue.job_type)

            jsoned_queues.append(q_dict)

        return {'queues': jsoned_queues}

    def put(self):
        queue_dict = json.loads(request.data)
        queue_name = queue_dict['job_type']

        if len(Queue.objects(job_type=queue_name)) > 0:
            raise Exception('Queue with same job_type already exists')


        queue = Queue(**queue_dict)
        queue.save()


        return {'queue': queue.to_dict()}



class QueueResource(ExistingQueueResource):
    def get(self, job_type):
        pulled_job = Job._collection.find_and_modify(
            query={'job_type': job_type, 'status': JobStatus.pending},
            sort={'last_update': 1},
            update={'$set': {'status': JobStatus.pulled}},
            fields={'job_type': False, 'last_update': False},
            new=True
        )
        if not pulled_job:
            return

        pulled_job['job_id'] = str(pulled_job['_id'])
        del pulled_job['_id']


        return {'job': pulled_job }


    def post(self, job_type):
        descriptor = request.json.get('descriptor')
        assert descriptor

        input_files = request.json.get('input') or []

        callback = request.json.get('callback')
        replicate = request.json.get('multiply') or 1

        jobs = [
            Job(
                job_type=job_type,
                descriptor=descriptor,
                callback=callback,
                input=input_files
            )
            for _ in xrange(replicate)
        ]
        jobs = Job.objects.insert(jobs)


        if replicate == 1:
            return {'job': jobs[0].to_dict()}
        else:
            return {"job_ids": [str(j.pk) for j in jobs]}

    def delete(self, job_type):
        queue = Queue.objects.get(job_type=job_type)
        queue.delete()

        Job.objects(job_type=job_type).delete()




class QueueInfoResource(MetaschedulerResource):
    def get(self, job_type):
        if not queue_exists(job_type):
            return {'exists': False}

        return {'length': queue_length(job_type), 'exists': True}
