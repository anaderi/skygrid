import os
import json
import hashlib
from datetime import datetime

from flask import request
from werkzeug import secure_filename

from flask.ext.restful import Resource
from flask.ext.restful import fields, marshal_with

from .api import SkygridResource
from ..app import app
from ..models import Dataset


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def upload_file(ds_file):
    if not (ds_file and allowed_file(ds_file.filename)):
        raise Exception('Bad file!')

    filename = secure_filename(ds_file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    ds_file.save(path)
    return path


def hashfile(path):
    hasher = hashlib.sha512()
    blocksize = 65536

    afile = open(path, 'rb')
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


class DatasetList(SkygridResource):
    def get(self):
        if request.args['hash']:
            return Dataset.objects.get(filehash=request.args['hash']).to_dict()
        elif request.args['name']:
            return {
                'datasets': [
                    ds.to_dict() 
                    for ds in Dataset.objects(name=request.args['name'])
                ]
            }            
        else:
            return {
                'datasets': [ds.to_dict() for ds in Dataset.objects]
            }


    def put(self):
        data = request.form

        path = upload_file(request.files['dataset'])
        ds_hash = hashfile(path)

        ds = Dataset(
            name=data['name'],
            datatype=data['type'],
            path=path,
            filehash=ds_hash,
            upload_time=datetime.now()
        ).save()

        return ds.to_dict()


class DatasetDetail(SkygridResource):
    def get(self, ds_id):
        return Dataset.objects.get(pk=ds_id).to_dict()

    def delete(self, ds_id):
        ds = Dataset.objects.get(pk=ds_id)
        os.remove(ds.path)
        return Dataset.objects.get(pk=ds_id).delete()
