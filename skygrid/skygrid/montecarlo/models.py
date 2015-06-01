import os
from datetime import datetime

from mongoengine import *

from flask import current_app

class MonteCarlo(Document):
    jobs = DictField()

    descriptor = DictField(required=True)
    multiplier = IntField(required=True)

    created = DateTimeField(default=datetime.now)

    meta = {
        'indexes': ['created'],
        'ordering': ['-created'],
    }

    def to_dict(self):
        return {
            'montecarlo_id': str(self.pk),
            'descriptor': self.descriptor,
            'multiplier': self.multiplier,
            'created': self.created.strftime(current_app.config['TIME_FORMAT']),
            'jobs': self.jobs,
        }


    def __unicode__(self):
        return "{} : {}".format(self.pk, self.name)
