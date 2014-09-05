import json
import datetime

from flask import request, jsonify

from .main import app
from ..generic.models import Worker, Job, User


@app.route('/')
def index():
    return "Hello, world!"

@app.route('/<job_type>/add_job', methods=['POST'])
def add_job(job_type):
    try:
        job_dict = json.loads(request.data)

        job = Job(job_type=job_type, description=job_dict)
        job.save()

        return jsonify(success=True, job=job.to_dict())
    except Exception, e:
        return jsonify(success=False, exception=str(e))


@app.route('/get_jobs', methods=['GET'])
def distribute_jobs():
    try:
        n_job = request.args.get('njob') or 1 # how many jobs we need to return
        n_job = int(n_job)
        job_type = request.args.get('job_type')

        jsoned_jobs = []

        jobs = Job.objects(job_type=job_type)[:n_job]
        for job in jobs:
            jsoned_jobs.append(job.to_dict())
            job.delete()

        return jsonify(success=True, jobs=jsoned_jobs)


    except Exception, e:
        return jsonify(success=False, exception=str(e))

