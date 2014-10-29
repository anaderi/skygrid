import json
import datetime

import pymongo
from flask import request, jsonify
from flask.ext.restful import reqparse

from ..app import db
from ..models import *
from ..rabbit import (
    rmq_push_to_queue,
    rmq_pull_from_queue,
    rmq_delete_queue,
    rmq_queue_length,
    rmq_queue_create
)

from api import MetaschedulerResource, ExistingQueueResource, queue_exists


class QueueManagementResource(MetaschedulerResource):
    def get(self):
        jsoned_queues = []

        queues = db.session.query(Queue).all()

        for queue in queues:
            jsoned_queues.append(queue.to_dict())

        return {'queues': jsoned_queues}

    def put(self):
        queue_dict = json.loads(request.data)

        queue = Queue(**queue_dict)
        db.session.add(queue)
        db.session.commit()

        return {'queue': queue.to_dict()}



class QueueResource(ExistingQueueResource):
    def _get_queue(self, job_type):
        return db.session.query(Queue).filter(Queue.job_type==job_type).first()

    def get(self, job_type):
        job = rmq_pull_from_queue(job_type)

        if job:
            return {'job': job }

    def post(self, job_type):
        job_dict = json.loads(request.data)

        job = Job(job_type=job_type, descriptor=job_dict)
        db.session.add(job)
        db.session.commit()

        rmq_push_to_queue(job_type, json.dumps(job.to_dict()))

        return {'job': job.to_dict()}

    def delete(self, job_type):
        queue = self._get_queue(job_type)
        db.session.delete(queue)
        db.session.commit()
        
        rmq_delete_queue(job_type)



class QueueInfoResource(MetaschedulerResource):
    def get(self, job_type):
        if not queue_exists(job_type):
            return {'exists': False}

        return {'length': rmq_queue_length(job_type), 'exists': True}
