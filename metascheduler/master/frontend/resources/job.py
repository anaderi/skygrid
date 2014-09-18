import datetime

from flask import request, jsonify
from flask.ext.restful import reqparse

from ..models import Job
from api import MetaschedulerResource


class JobResource(MetaschedulerResource):
    def get(self, job_id):
        job = Job.objects.get(pk=job_id)
        return {'jobs': job.to_dict()}


    def post(self, job_id):
        job = Job.objects.get(pk=job_id)
        
        new_status = request.form['status'] if request.form['status'] else ""
        if new_status not in Job.VALID_STATUSES:
            raise ValueError("Invalid status")

        job.status = request.form['status']
        job.assigned_worker.last_seen = datetime.datetime.now()
        job.last_update = datetime.datetime.now()
        job.save()

        return {'jobs': job.to_dict()}
