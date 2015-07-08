import os
import json
from datetime import datetime

from flask import request, current_app

from ..api import SkygridResource

from .models import MonteCarlo
from .helpers import check_update_valid, update_document

class MonteCarloList(SkygridResource):
    def get(self):
        limit = int(request.args.get('limit') or "0")
        skip  = int(request.args.get('skip') or "0")

        if skip == limit == 0:
            return {
                "mc_objects": MonteCarlo.objects.count(),
                "note": "Use `limit` and `skip` GET-parameters to obtain results"
            }

        assert limit > 0, "`limit` should be >0"
        mcs = MonteCarlo.objects().skip(skip).limit(limit)
        return [mc.to_dict() for mc in mcs]


    def put(self):
        data = request.json

        mc = MonteCarlo(
            descriptor=data['descriptor'],
            multiplier=data['multiplier'] or 1,
            input=data.get('input') or []
        ).save()


        queue_name = current_app.config['MC_QUEUE']
        queue = current_app.metascheduler.queue(queue_name)

        callback_url = os.path.join(
            current_app.config['CALLBACK_URL'],
            "montecarlo",
            str(mc.pk),
            "callback"
        )

        jobs = queue.put({
            'descriptor': mc.descriptor,
            'callback':  callback_url,
            'multiply': mc.multiplier,
            'input': mc.input
        })

        mc.jobs = {job_id : "in_queue" for job_id in jobs}

        mc.save()

        return mc.to_dict()


class MonteCarloDetail(SkygridResource):
    def get(self, mc_id):
        return MonteCarlo.objects.get(pk=mc_id).to_dict()

    def delete(self, mc_id):
        return MonteCarlo.objects.get(pk=mc_id).delete()


class MonteCarloCallback(SkygridResource):
    def post(self, mc_id):
        mc = MonteCarlo.objects.get(pk=mc_id)
        job = request.json
        job_id = job['job_id']

        if not job_id in mc.jobs:
            raise Exception("Job is not in this MC.")

        mc.jobs[job_id] = job['status']
        mc.save()

        return "ok"


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class MonteCarloRefresh(SkygridResource):
    def post(self, mc_id):
        mc = MonteCarlo.objects.get(pk=mc_id)

        for jobs_chunk in chunks(mc.jobs.keys(), current_app.config['JOBS_UPDATE_CHUNK_SIZE']):
            statuses = current_app.metascheduler.get_statuses(jobs_chunk)
            mc.jobs.update(statuses)

        mc.save()

        return "updated"

class MonteCarloJobs(SkygridResource):
    def get(self, mc_id):
        return MonteCarlo.objects.get(pk=mc_id).jobs
