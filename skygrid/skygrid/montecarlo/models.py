import os
from datetime import datetime

from mongoengine import *

from flask import current_app


class JobStatus:
    pending = "pending"
    running = "running"
    failed  = "failed"
    completed = "completed"
    pulled = "pulled"

    valid_statuses = set([pending, running, failed, completed, pulled])


class MonteCarlo(Document):
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
                status: statuses.count(status) for status in JobStatus.valid_statuses
            },
        }


    def __unicode__(self):
        return "{} : {}".format(self.pk, self.name)
