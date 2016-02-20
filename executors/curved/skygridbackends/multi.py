from .base import BackendBase
from urlparse import urlparse

class MultiBackend(BackendBase):
    def __init__(self, mapper):
        self.mapper = mapper

    def parse_uri(self, uri):
        uri = urlparse(uri)
        backend = self.mapper.get(uri.scheme)
        assert backend

        return backend, uri.path, uri.scheme

    def copy_from_backend(self, src_uri, dst_path):
        backend, src_path, _ = self.parse_uri(src_uri)
        backend.copy_from_backend(src_path, dst_path)

    def copy_to_backend(self, src_path, dst_uri):
        backend, dst_path, _ = self.parse_uri(dst_uri)
        backend.copy_to_backend(src_path, dst_path)

    def list_uploaded(self, uri):
        backend, path, scheme = self.parse_uri(uri)
        return ["{}:{}".format(scheme, f) for f in backend.list_uploaded(path)]
