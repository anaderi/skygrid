import os
import json
from datetime import datetime

from flask import request, current_app

from ..api import SkygridResource

from .models import MonteCarlo
from .helpers import check_update_valid, update_document

class MonteCarloList(SkygridResource):
    def get(self):
        return [mc.to_dict() for mc in MonteCarlo.objects.all()]


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