import os
import time

from mongoengine import *

class Dataset(Document):
    name = StringField(required=True)
    path = StringField(required=True)
    datatype = StringField(required=True)
    upload_time = DateTimeField(required=True)
    filehash = StringField(required=True, unique=True)

    meta = {
        'ordering': ['upload_ts'],
        'indexes': ['filehash', 'name']
    }

    def to_dict(self):
        return {
            'id': str(self.pk),
            'name': self.name,
            'type': self.datatype,
            'hash': self.filehash,
            'uploaded': str(self.upload_time)
        }


    def __unicode__(self):
        return "{} : {}".format(self.pk, self.name)
