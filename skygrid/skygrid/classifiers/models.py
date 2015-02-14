import os
import time

from mongoengine import *

from ..datasets.models import Dataset

from flask import current_app

class Classifier(Document):
    dataset = ReferenceField(Dataset)

    description = StringField(required=True)
    classifier_type = StringField(required=True)
    parameters = DictField()
    created = DateTimeField()

    job_id = StringField()
    status = StringField()

    meta = {
        'indexes': ['description', 'classifier_type'],
        'ordering': ['-created'],
    }

    def to_dict(self):
        if isinstance(self.dataset, Dataset):
            ds_id = str(self.dataset.pk)
        else:
            ds_id = "DELETED"

        return {
            'classifier_id': str(self.pk),
            'dataset_id': ds_id,
            'description': self.description,
            'type': self.classifier_type,
            'parameters': self.parameters,
            'status': self.status,
            'created': self.created.strftime(current_app.config['TIME_FORMAT']),
            'training_job_id': self.job_id
        }


    def __unicode__(self):
        return "{} : {}".format(self.pk, self.name)
