import os
from datetime import datetime

from mongoengine import *

from flask import current_app

class MonteCarlo(Document):
    jobs = ListField(StringField())
    completed_jobs = IntField(min_value=0, default=0)
    failed_jobs = IntField(min_value=0, default=0)

    descriptor = DictField(required=True)
    multiplier = IntField(required=True)

    created = DateTimeField(default=datetime.now)

    status = StringField()

    meta = {
        'indexes': ['created', 'status'],
        'ordering': ['-created'],
    }

    def to_dict(self):
        return {
            'montecarlo_id': str(self.pk),
            'descriptor': self.descriptor,
            'multiplier': self.multiplier,
            'created': self.created.strftime(current_app.config['TIME_FORMAT']),
            'status': self.status,
            'jobs': self.jobs,
            'completed': self.completed_jobs,
            'failed': self.failed_jobs
        }


    def __unicode__(self):
        return "{} : {}".format(self.pk, self.name)
