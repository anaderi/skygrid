import os
import datetime

from mongoengine import *


def generate_salt():
    return os.urandom(128).encode('base_64')[:-1] # "\n" always at the end


class User(Document):
    username = StringField(unique=True)
    pass_hash = StringField(default="") # PBKDF2
    salt = StringField(default=generate_salt)
    info = DictField()

    def __unicode__(self):
        return "{}".format(self.username)


class Worker(Document):
    wid = IntField(unique=True)
    hostname = StringField()
    last_seen = DateTimeField(default=datetime.datetime.now)
    info = DictField()

    active = BooleanField(default=False)

    meta = {
        'indexes': ['wid', 'last_seen', 'active'],
    }

    def to_dict(self):
        return {
            "wid": self.wid,
            "hostname": self.hostname,
            "last_seen": self.last_seen,
            "info": self.info,

            "active": self.active,
        }

    def __unicode__(self):
        return "{} : {}".format(self.wid, self.hostname)


class Job(Document):
    name = StringField()
    environments = ListField(StringField())
    owner = ReferenceField(User)
    app = StringField()

    workdir = StringField()
    cmd = StringField()
    args = DictField()

    run_containters = IntField(min_value=1)
    min_memoryMB = IntField(min_value=1)
    max_memoryMB = IntField(min_value=1)
    cpu_per_container = IntField()

    assigned_worker = ReferenceField(Worker)
    submitted = DateTimeField(default=datetime.datetime.now)
    last_update = DateTimeField(default=datetime.datetime.now)

    VALID_STATUSES = ['submitted', 'running', 'completed', 'failed']
    status = StringField(default="submitted") # submitted, running, complete, failed

    meta = {
        'indexes': ['name', 'owner', 'app'],
        'ordering': ['submitted']
    }

    def to_dict(self):
        return {
            "id": str(self.pk),
            "worker":  self.assigned_worker.wid if self.assigned_worker else None,

            "name": self.name,
            "environments": self.environments,
            "owner": self.owner.username,
            "app": self.app,

            "workdir": self.workdir,
            "cmd": self.cmd,
            "args": self.args,

            "run_containters": self.run_containters,
            "min_memoryMB": self.min_memoryMB,
            "max_memoryMB": self.max_memoryMB,
            "cpu_per_container": self.cpu_per_container,

            "submitted": self.submitted,
            "status": self.status,
        }

    def __unicode__(self):
        return "{} : {}".format(self.pk, self.name)