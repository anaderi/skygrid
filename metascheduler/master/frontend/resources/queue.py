import json
import datetime

from flask import request, jsonify
from flask.ext.restful import Resource, reqparse

from ...generic.models import Job



class QueueResource(Resource):
    def get(self, job_type):
        try:
            n_job = int(request.args.get('njob') or 1) # how many jobs we need to return

            jsoned_jobs = []

            jobs = Job.objects(job_type=job_type)[:n_job]

            for job in jobs:
                jsoned_jobs.append(job.to_dict())
                job.delete()

            return jsonify(success=True, jobs=jsoned_jobs)


        except Exception, e:
            return jsonify(success=False, exception=str(e))

    def post(self, job_type):
        try:
            job_dict = json.loads(request.data)

            job = Job(job_type=job_type, description=job_dict)
            job.save()

            return jsonify(success=True, job=job.to_dict())
        except Exception, e:
            return jsonify(success=False, exception=str(e))


class QueueLengthResource(Resource):
    def get(self, job_type):
        try:
            l = len(Job.objects(job_type=job_type))

            return jsonify(success=True, length=l)
        except Exception, e:
            return jsonify(success=False, exception=str(e))
