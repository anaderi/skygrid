import os
from datetime import datetime

from mongoengine import *

from flask import current_app

VALID_STATUSES =  ["failed", "running", "pulled", "completed", "pending"]

class MonteCarlo(Document): # Add the class and its methods descriptions.
    jobs = DictField()

    descriptor = DictField(required=True)
    multiplier = IntField(required=True)

    input = ListField(StringField())


    created = DateTimeField(default=datetime.now)

    meta = {
        'indexes': ['created'],
        'ordering': ['-created'],
    }

    def to_dict(self):
        statuses = self.jobs.values()
        return {
            'montecarlo_id': str(self.pk),
            'descriptor': self.descriptor,
            'multiplier': self.multiplier,
            'created': self.created.strftime(current_app.config['TIME_FORMAT']),
            'jobs': {
                status: statuses.count(status) for status in VALID_STATUSES
            },
        }


    def __unicode__(self):
        return "{}".format(self.pk)
