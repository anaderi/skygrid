import datetime

from flask import request, jsonify
from flask.ext.restful import Resource, reqparse

from ...generic.models import Job


class JobResource(Resource):
    def get(self, job_id):
        try:
            job = Job.objects.get(pk=job_id)
            return jsonify(success=True, jobs=job.to_dict())
        except Exception, e:
            return jsonify(success=False, exception=str(e))

    def post(self, job_id):
        try:
            job = Job.objects.get(pk=job_id)
            
            new_status = request.form['status'] if request.form['status'] else ""
            if new_status not in Job.VALID_STATUSES:
                raise ValueError("Invalid status")

            job.status = request.form['status']
            job.assigned_worker.last_seen = datetime.datetime.now()
            job.last_update = datetime.datetime.now()
            job.save()

            return jsonify(success=True, jobs=job.to_dict())
        except Exception, e:
            return jsonify(success=False, exception=str(e))
