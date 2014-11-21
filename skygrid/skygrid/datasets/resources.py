import os
import hashlib
import shutil
from datetime import datetime

from flask import request, current_app
from werkzeug import secure_filename

from ..api import SkygridResource
from .blueprint import blueprint

from .models import Dataset


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


def upload_file(ds_id, ds_file):
    if not (ds_file and allowed_file(ds_file.filename)):
        raise Exception('Bad file!')

    ds_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], ds_id)
    os.mkdir(ds_dir)

    filename = secure_filename(ds_file.filename)
    path = os.path.join(ds_dir, filename)
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
        if 'hash' in request.args:
            return {
                'datasets': [
                    ds.to_dict()
                    for ds in Dataset.objects(filehash=request.args['hash'])
                ]
            }
        elif 'name' in request.args:
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
        ds_embryo = Dataset(
            name=data['name'],
            datatype=data['type']
        ).save()

        try:
            path = upload_file(str(ds_embryo.pk), request.files['dataset'])
            ds_hash = hashfile(path)
        except Exception, e:
            ds_embryo.delete()
            raise Exception(e)
        else:
            ds_embryo.path = path
            ds_embryo.filehash = ds_hash
            ds_embryo.upload_time = datetime.now()
            ds_embryo.save()

            return ds_embryo.to_dict()


class DatasetDetail(SkygridResource):
    def get(self, ds_id):
        return Dataset.objects.get(pk=ds_id).to_dict()

    def delete(self, ds_id):
        ds = Dataset.objects.get(pk=ds_id)
        ds_workdir = os.path.dirname(ds.path)
        shutil.rmtree(ds_workdir)

        return ds.delete()
