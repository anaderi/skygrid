import os
import json
import hashlib
import shutil
from datetime import datetime

from flask import request, current_app, send_file
from werkzeug import secure_filename

from ..api import *

from .blueprint import blueprint
from .models import Classifier, Dataset
from .helpers import check_update_valid, update_document

class ClassifierList(SkygridResource):
    def get(self):
        return {
            'classifiers': [cl.to_dict() for cl in Classifier.objects.all()]
        }


    def put(self):
        data = request.json


        cl = Classifier(
            description=data['description'],
            classifier_type=data['type'],
            parameters=data['parameters'],
            dataset=Dataset.objects.get(pk=data['dataset']),
            status="not_trained",
            created=datetime.now()
        ).save()

        if data.get('start_train') == False:
            return cl.to_dict()

        queue_name = 'classifier_' + cl.classifier_type
        queue = current_app.metascheduler.queue(queue_name)

        callback_url = os.path.join(
            current_app.config['CALLBACK_URL'],
            "classifiers",
            str(cl.pk),
            "callback"
        )

        job = queue.put({
            'descriptor': {
                'classifier_id': str(cl.pk)
            },
            'callback':  callback_url
        })

        cl.status = "in_queue"
        cl.job_id = job.job_id
        cl.save()

        return cl.to_dict()


class ClassifierDetail(SkygridResource):
    def get(self, cl_id):
        return Classifier.objects.get(pk=cl_id).to_dict()

    def post(self, cl_id):
        update_data = request.json
        check_update_valid(update_data)

        cl = Classifier.objects.get(pk=cl_id)
        update_document(cl, update_data)

        cl.save()

        return cl.to_dict()

    def delete(self, cl_id):
        return Classifier.objects.get(pk=cl_id).delete()


class ClassifierCallback(SkygridResource):
    def get_classifier_status(self, job_status):
        statuses = {
            "pending" : 'in_queue',
            "running" : 'training',
            "failed" : 'failed_to_train',
            "completed" : 'trained',
        }

        return statuses[job_status]

    def post(self, cl_id):
        data = request.json

        cl = Classifier.objects.get(pk=cl_id)
        assert cl.job_id == data['job_id']

        cl.status = self.get_classifier_status(data['status'])
        cl.save()


class ClassifierFormula(Resource):
    def get(self, cl_id):
        cl = Classifier.objects.get(pk=cl_id)
        job = current_app.metascheduler.job(cl.job_id, from_api=True)

        formula_path = job.descriptor.get('output_formula')
        if not formula_path:
            return

        return send_file(formula_path)
