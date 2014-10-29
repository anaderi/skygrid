import os
import time
import json
import uuid

from .app import db

from sqlalchemy.types import TypeDecorator, CHAR, VARCHAR
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


# User model and stuff used
# def generate_salt():
#     return os.urandom(128).encode('base_64')[:-1] # "\n" always at the end


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     pass_hash = db.Column(db.String(80)) # PBKDF2
#     salt = db.Column(db.String(174))
#     info = db.Column(db.Text)

#     def __init__(self, username, email):
#         self.username = username
#         self.email = email
#         self.salt = generate_salt()


#     def __repr__(self):
#         return '<User %r>' % self.username


# Queue model and stuff used

class Queue(db.Model):
    job_type = db.Column(db.String, primary_key=True)
    # jobs = relationship("Job")

    timeout = db.Column(db.Float)
    use_timeout = db.Column(db.Boolean, default=False)

    def __init__(self, job_type, timeout=None):
        self.job_type = job_type
        if timeout:
            self.use_timeout = True
            self.timeout = timeout

    def to_dict(self):
        d =  {
            "name": self.job_type,
            "use_timeout": self.use_timeout,
        }

        if self.use_timeout:
            d['timeout'] = self.timeout

        return d

    def __repr__(self):
        timeout = self.timeout if self.use_timeout else "none"
        return "{} : timeout={}".format(self.job_type, timeout)



# Job model and stuff used

class JobStatus:
    pending = "pending"
    running = "running"
    failed  = "failed"

    valid_statuses = set([pending, running, failed])

def get_current_time():
    return time.time()


class Job(db.Model):
    job_id = db.Column(db.VARCHAR, index=True, primary_key=True, unique=True)
    job_type = ForeignKey('queue.job_type')

    descriptor = db.Column(JSONEncodedDict, default="")

    status = db.Column(db.Enum(*JobStatus.valid_statuses), default=JobStatus.pending)
    last_update = db.Column(db.Float, default=get_current_time, index=True)

    def __init__(self, job_type, descriptor):
        self.job_type = job_type
        self.descriptor = descriptor
        self.job_id = uuid.uuid4().hex

        while Job.query.filter(Job.job_id == self.job_id).count() != 0:
            self.job_id = uuid.uuid4().hex

    def to_dict(self):
        d = {
            'job_id': str(self.job_id),
            'status': self.status,
            'descriptor': self.descriptor
        }

        return d

    def __repr__(self):
        return "{} : {}".format(self.job_id, self.job_type)

