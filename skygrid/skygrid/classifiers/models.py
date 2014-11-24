import os
import time

from mongoengine import *

from ..datasets.models import Dataset

class Classifier(Document):

    description = StringField(required=True)
    classifier_type = StringField(required=True)
    parameters = DictField()
    dataset = ReferenceField(Dataset)
    status = StringField()

    meta = {
        'indexes': ['description', 'classifier_type']
    }

    def to_dict(self):
        return {
            'id': str(self.pk),
            'description': self.description,
            'type': self.classifier_type,
            'dataset_id': str(self.dataset.pk),
            'parameters': self.parameters,
            'status': self.status
        }


    def __unicode__(self):
        return "{} : {}".format(self.pk, self.name)
