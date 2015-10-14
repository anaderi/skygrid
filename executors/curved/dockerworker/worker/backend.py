import os
import shutil
import errno
from urlparse import urlparse

import easywebdav
from git import Repo

from ..config import config


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


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

        try:
            shutil.copy(src_path, dst_path)
        except:
            shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)

    def copy_to_backend(self, src_path, dst_path):
        assert os.path.exists(src_path)

        mkdir_p(dst_path)

        try:
            shutil.copytree(src_path, dst_path)
        except:
            shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)

    def list_uploaded(self, path):
        for root, dirs, files in os.walk(path):
            for basename in files:
                filename = os.path.join(root, basename)
                yield filename


class WebDAVBackend(BackendBase):
    def __init__(self, host, params):
        self.wc = easywebdav.connect(host, **params)

    def copy_from_backend(self, src_path, dst_path):
        if os.path.isdir(dst_path):
            basename = src_path.split("/")[-1]
            dst_path = os.path.join(dst_path, basename)

        self.wc.download(src_path, dst_path)

    def copy_to_backend(self, src_path, dst_path):
        assert os.path.exists(src_path)

        self.wc.mkdirs(dst_path)

        for root, dirs, files in os.walk(src_path):
            for basename in files:
                filename = os.path.join(root, basename)

                self.wc.upload(filename, os.path.join(dst_path, basename))


    def list_uploaded(self, path):
        return [f.name for f in self.wc.ls(path)]


class GitBackend(BackendBase):
    def copy_from_backend(self, src_path, dst_path):
        Repo.clone_from(src_path, dst_path, recursive=True)

    def copy_to_backend(self, src_path, dst_path):
        raise NotImplementedError

    def list_uploaded(self, path):
        raise NotImplementedError



BACKENDS = {
    "local" : LocalBackend(),
    "dcache": WebDAVBackend(config.DCACHE_HOST, config.DCACHE_PARAMS),
    "git": GitBackend(),
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
