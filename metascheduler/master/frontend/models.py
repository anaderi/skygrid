import os
import time

from mongoengine import *

# User model and stuff used

def generate_salt():
    return os.urandom(128).encode('base_64')[:-1] # "\n" always at the end


class User(Document):
    username = StringField(unique=True)
    pass_hash = StringField(default="") # PBKDF2
    salt = StringField(default=generate_salt)
    info = DictField()

    def __unicode__(self):
        return "{}".format(self.username)


# Job model and stuff used

from libscheduler.job import JobStatus

def get_current_time():
    return time.time()


class Job(Document):
    job_type = StringField(default="ANY")
    description = DictField(default={})

    status = StringField(default=JobStatus.pending)
    last_update = FloatField(min_value=0, default=get_current_time)

    meta = {
        'ordering': ['last_update']
    }

    def to_dict(self):
        d = {
            'id': str(self.pk),
            'status': self.status,
            'description': self.description
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
