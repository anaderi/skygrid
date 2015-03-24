import json
from datetime import datetime

import gevent
from gevent import thread, queue

from flask import request
from api import MetaschedulerResource

import requests

from ..models import Job, JobStatus


def do_callback(job):
    if job.callback:
        requests.post(
                job.callback,
                data=json.dumps(job.to_dict()),
                headers={'content-type': 'application/json'}
        )


class JobResource(MetaschedulerResource):
    def get(self, job_id):
        if ',' in job_id:
            return {
              job_id: Job.objects.get(pk=job_id).to_dict() for job_id in job_id.split(',')
            }
        else:
            return Job.objects.get(pk=job_id).to_dict()

    def delete(self, job_id):
        job = Job.objects.get(pk=job_id)
        job.delete()


class JobStatusResource(MetaschedulerResource):
    def get(self, job_id):
        return {
            'status': Job.objects.get(pk=job_id).status
        }

    def post(self, job_id):
        update_dict = request.json
        new_status = update_dict.get('status')

        assert new_status in JobStatus.valid_statuses

        job = Job.objects.get(pk=job_id)
        job.status = new_status
        job.save()

        if job.callback:
            gevent.spawn(do_callback, job).start()

        return {'updated_status': job.status}


class JobOutputResource(MetaschedulerResource):
    def get(self, job_id):
        return {
            'output': Job.objects.get(pk=job_id).output
        }

    def post(self, job_id):
        update_dict = request.json
        new_output = update_dict.get('output')

        job = Job.objects.get(pk=job_id)
        job.output = new_output
        job.save()

        return {'updated_output': job.output}


class JobInputResource(MetaschedulerResource):
    def get(self, job_id):
        return {
            'input': Job.objects.get(pk=job_id).input
        }


class JobDebugResource(MetaschedulerResource):
    def get(self, job_id):
        return {
            'debug': Job.objects.get(pk=job_id).debug
        }

    def post(self, job_id):
        update_dict = request.json

        job = Job.objects.get(pk=job_id)
        job.debug = update_dict
        job.save()

        if job.callback:
            gevent.spawn(do_callback, job).start()

        return job.to_dict()
