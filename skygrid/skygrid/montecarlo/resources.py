import os
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
            multiplier=data['multiplier'],
            status="not_submitted",
        ).save()


        queue_name = current_app.config['MC_QUEUE']
        queue = current_app.metascheduler.queue(queue_name)

        callback_url = os.path.join(
            current_app.config['CALLBACK_URL'],
            "montecarlo",
            str(mc.pk),
            "callback"
        )

        mc.jobs = queue.put({
            'descriptor': mc.descriptor,
            'callback':  callback_url,
            'multiply': mc.multiplier,
        })

        mc.status = "in_queue"
        mc.save()

        return mc.to_dict()


class MonteCarloDetail(SkygridResource):
    def get(self, mc_id):
        return MonteCarlo.objects.get(pk=mc_id).to_dict()

    def delete(self, mc_id):
        return MonteCarlo.objects.get(pk=mc_id).delete()


class MonteCarloCallback(SkygridResource):
    def post(self, mc_id):
        print "Got callback for {}: \n {}".format(mc_id, reque.json)