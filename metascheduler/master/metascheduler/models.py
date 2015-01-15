import os
import time
from datetime import datetime

from mongoengine import *


# Job model and stuff used

class JobStatus:
    pending = "pending"
    running = "running"
    failed  = "failed"
    completed = "completed"
    pulled = "pulled"

    valid_statuses = set([pending, running, failed, completed, pulled])


class Job(Document):
    job_type = StringField(default="ANY")
    descriptor = DictField(default={})

    status = StringField(default=JobStatus.pending)
    last_update = DateTimeField(default=datetime.now)

    callback = StringField()

    meta = {
        'ordering': ['last_update'],
        'indexes': ['job_type', 'status', 'last_update']
    }

    def to_dict(self):
        d = {
            'job_id': str(self.pk),
            'status': self.status,
            'descriptor': self.descriptor
        }

        return d

    def __unicode__(self):
        return "{} : {}".format(self.pk, self.job_type)


# Queue model and stuff used

class Queue(Document):
    job_type = StringField(required=True, unique=True)

    timeout = FloatField(min_value=0)
    use_timeout = BooleanField(default=False, required=True)

    def to_dict(self):
        d =  {
            "name": self.job_type,
            "use_timeout": self.use_timeout,
        }

        if self.use_timeout:
            d['timeout'] = self.timeout

        return d

    def __unicode__(self):
        timeout = self.timeout if self.use_timeout else "none"
        return "{} : timeout={}".format(self.job_type, timeout)
