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
    last_seen = FloatField()
    info = DictField()

    active = BooleanField(default=False)

    meta = {
        'indexes': ['wid', 'last_seen', 'active'],
    }

    def __unicode__(self):
        return "{} : {}".format(self.wid, self.hostname)


class Task(Document):
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
    status = StringField(default="submitted") # submitted, running, complete, failed

    meta = {
        'indexes': ['name', 'owner', 'app'],
        'ordering': ['submitted']
    }