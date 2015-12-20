import os
import time

from mongoengine import *

from flask import current_app

class Dataset(Document):
    name = StringField(required=True)
    path = StringField()
    datatype = StringField(required=True)
    upload_time = DateTimeField()
    filehash = StringField()

    meta = {
        'ordering': ['upload_ts'], # maybe upload_time?
        'indexes': ['filehash', 'name']
    }

    def to_dict(self):
        return {
            'id': str(self.pk),
            'name': self.name,
            'type': self.datatype,
            'hash': self.filehash,
            'uploaded': self.upload_time.strftime(current_app.config['TIME_FORMAT']),
        }


    def __unicode__(self):
        return "{} : {}".format(self.pk, self.name)
