import os
import json
import hashlib
import shutil
from datetime import datetime

from flask import request, current_app
from werkzeug import secure_filename

from ..api import SkygridResource
from .blueprint import blueprint

from .models import Classifier, Dataset


class ClassifierList(SkygridResource):
    def get(self):
        return {
            'classifiers': [cl.to_dict() for cl in Classifier.objects]
        }


    def put(self):
        data = request.json


        cl = Classifier(
            description=data['description'],
            classifier_type=data['type'],
            parameters=data['parameters'],
            dataset=Dataset.objects.get(pk=data['dataset']),
            status="not_trained"
        ).save()

        if data.get('start_train') == False:
            return cl.to_dict()

        queue_name = 'classifier_' + cl.classifier_type
        queue = current_app.metascheduler.queue(queue_name)
        queue.put(cl.to_dict())

        cl.status = "in_queue"
        cl.save()

        return cl.to_dict()


class ClassifierDetail(SkygridResource):
    def get(self, cl_id):
        return Classifier.objects.get(pk=cl_id).to_dict()

    def delete(self, cl_id):
        return Classifier.objects.get(pk=cl_id).delete()
