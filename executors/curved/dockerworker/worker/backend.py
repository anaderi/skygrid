import os
import shutil

from urlparse import urlparse



class BackendBase(object):
    def copy_from_backend(self, src_path, dst_path):
        raise NotImplementedError()

    def copy_to_backend(self, src_path, dst_path):
        raise NotImplementedError()


class LocalBackend(BackendBase):
    def copy_from_backend(self, src_path, dst_path):
        assert os.path.exists(src_path)
        assert os.path.isfile(src_path)

        shutil.copy(src_path, dst_path)

    def copy_to_backend(self, src_path, dst_path):
        assert os.path.exists(src_path)
        assert os.path.isfile(src_path)

        if not os.path.isdir(dst_path):
            os.makedirs(dst_path)

        shutil.copy(src_path, dst_path)


BACKENDS = {
    "local" : LocalBackend()
}


def copy_from_backend(src_uri, dst_path):
    uri = urlparse(src_uri)
    backend = BACKENDS.get(uri.scheme)
    assert backend

    backend.copy_from_backend(uri.path, dst_path)

def copy_to_backend(src_path, dst_uri):
    uri = urlparse(dst_uri)
    backend = BACKENDS.get(uri.scheme)
    assert backend

    backend.copy_to_backend(src_path, uri.path)
