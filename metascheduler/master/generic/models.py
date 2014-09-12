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
    job_type = StringField(default="ANY")
    description = DictField(default={})

    def to_dict(self):
        return self.description

    def __unicode__(self):
        return "{} : {}".format(self.pk, self.job_type)


class Queue(Document):
    job_type = StringField(required=True)
    
    timeout = IntField(min_value=0)
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
