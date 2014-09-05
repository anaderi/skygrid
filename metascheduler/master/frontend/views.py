import json
import datetime

from flask import request, jsonify

from .main import app
from ..generic.models import Worker, Job, User


# from tasks import *


@app.route('/')
def index():
    return "Hello, world!"


@app.route('/beat/<int:wid>')
def worker_heartbeat(wid):
    worker, created = Worker.objects.get_or_create(
        wid=wid, 
        defaults={
            'hostname': request.remote_addr,
            'meta': {},
            'active': True
        }
    )

    if not created:
        worker.last_seen = datetime.datetime.now()
        worker.active = True
        worker.save()

    return jsonify(success=True, worker=worker.to_dict())


@app.route('/add_job', methods=['POST'])
def add_job():
    try:
        job_dict = json.loads(request.data)
        job_dict['owner'] = User.objects.get(username=job_dict['owner'])

        job = Job(**job_dict)
        job.save()

        return jsonify(success=True, job=job.to_dict())
    except Exception, e:
        return jsonify(success=False, exception=str(e))


@app.route('/get_jobs', methods=['GET'])
def distribute_jobs():
    try:
        worker = Worker.objects.get(wid=int(request.args.get('wid')))
        n_job = int(request.args.get('njob')) or 1 # how many jobs we need to return

        jsoned_jobs = []

        jobs = Job.objects(assigned_worker=None)[:n_job]
        print len(jobs)
        for job in jobs:
            job.assigned_worker = worker
            jsoned_jobs.append(job.to_dict())

            job.save()

        return jsonify(success=True, jobs=jsoned_jobs)


    except Exception, e:
        return jsonify(success=False, exception=str(e))

