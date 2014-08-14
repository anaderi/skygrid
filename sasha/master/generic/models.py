from mongoengine import *

class Worker(Document):
    wid = IntField(unique=True)
    hostname = StringField()
    last_seen = FloatField()
    meta = DictField()

    meta = {
        'indexes': ['wid'],
    }

    def __unicode__(self):
        return "{} : {}".format(self.wid, self.hostname)
