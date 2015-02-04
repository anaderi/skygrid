import os
import hashlib
import shutil
from datetime import datetime

from flask import request, current_app
from werkzeug import secure_filename

from ..api import SkygridResource
from .blueprint import blueprint

from .models import Dataset


def get_extension(filename):
    assert '.' in filename
    return filename.rsplit('.', 1)[1]

def allowed_extension(extension):
    return extension in current_app.config['ALLOWED_EXTENSIONS']


def upload_file(ds_id, ds_file):
    extension = get_extension(ds_file.filename)
    if not allowed_extension(extension):
        raise Exception('Bad file!')

    ds_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], ds_id)
    os.mkdir(ds_dir)

    filename = "data." + extension
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

        path, ds_hash = data.get('uri'), data.get('hash')
        if not path:
            try:
                path = upload_file(str(ds_embryo.pk), request.files['dataset'])
                ds_hash = hashfile(path)
            except Exception, e:
                ds_embryo.delete()
                raise Exception(e)

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

        if os.path.isfile(ds.path):
            ds_workdir = os.path.dirname(ds.path)
            shutil.rmtree(ds_workdir)

        return ds.delete()
