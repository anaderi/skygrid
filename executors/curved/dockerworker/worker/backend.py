import os
import shutil

from urlparse import urlparse



class BackendBase(object):
    def copy_from_backend(self, src_path, dst_path):
        raise NotImplementedError()

    def copy_to_backend(self, src_path, dst_path):
        raise NotImplementedError()

    def list_uploaded(self, path):
        raise NotImplementedError()


class LocalBackend(BackendBase):
    def copy_from_backend(self, src_path, dst_path):
        assert os.path.exists(src_path)
        assert os.path.isfile(src_path)

        shutil.copy(src_path, dst_path)

    def copy_to_backend(self, src_path, dst_path):
        assert os.path.exists(src_path)

        shutil.copytree(src_path, dst_path)

    def list_uploaded(self, path):
        for root, dirs, files in os.walk(path):
            for basename in files:
                filename = os.path.join(root, basename)
                yield filename


BACKENDS = {
    "local" : LocalBackend()
}

def parse_uri(uri):
    uri = urlparse(uri)
    backend = BACKENDS.get(uri.scheme)
    assert backend

    return backend, uri.path, uri.scheme


def copy_from_backend(src_uri, dst_path):
    backend, src_path, _ = parse_uri(src_uri)
    backend.copy_from_backend(src_path, dst_path)


def copy_to_backend(src_path, dst_uri):
    backend, dst_path, _ = parse_uri(dst_uri)
    backend.copy_to_backend(src_path, dst_path)


def list_uploaded(uri):
    backend, path, scheme = parse_uri(uri)
    return ["{}:{}".format(scheme, f) for f in backend.list_uploaded(path)]
