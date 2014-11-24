import os
import hashlib

from common import *


def hashfile(path):
    hasher = hashlib.sha512()
    blocksize = 65536

    afile = open(path, 'rb')
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


class Dataset(object):

    def __init__(self, api_url, ds_id=None, path=None, name=None):
        self.api_url = u(api_url)
        self.ds_url = self.api_url + "datasets"

        if ds_id:
            self.ds_id = ds_id
            self.load_from_api()
        elif path:
            if not os.path.isfile(path):
                raise Exception('Could not access file on {}'.format(path))

            self.path = path
            self.name = name
            self.load_from_path()
        else:
            raise Exception("Neither ds_id nor path sepcified")


    def load_from_path(self):
        if not self.name:
            self.name = os.path.basename(self.path)

        fileName, fileExtension = os.path.splitext(self.path)
        self.filetype = fileExtension[1:] # '.csv' -> 'csv'
        self.filehash = hashfile(self.path)


    def load_from_api(self):
        data = sg_get(self.ds_url + self.ds_id)

        self.filehash = data['hash']
        self.ds_id = data['id']
        self.name = data['name']
        self.filetype = data['type']
        self.uploaded_at = data['uploaded']


    def upload(self):
        payload = {
            'name': self.name,
            'type': self.filetype,
        }
        files = {'dataset': open(self.path, 'rb')}

        result = sg_put(
            self.ds_url,
            data=payload,
            files=files
        )

        self.ds_id = result['id']
        self.uploaded_at = result['uploaded']

        return True


    def delete(self):
        if not hasattr(self, 'ds_id'):
            raise Exception('Dataset id is not set. Seems like dataset is not uploaded.')

        result = sg_delete(self.ds_url + self.ds_id)
        assert result == {}

        return True



    def __eq__(self, other):
        return all((
            (self.filehash == other.filehash),
            (self.ds_id == other.ds_id),
            (self.name == other.name),
            (self.filetype == other.filetype),
            (self.uploaded_at == other.uploaded_at),
        ))