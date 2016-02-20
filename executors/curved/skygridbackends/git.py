from __future__ import absolute_import

from git import Repo
from .base import BackendBase

class GitBackend(BackendBase):
    def copy_from_backend(self, src_path, dst_path):
        Repo.clone_from(src_path, dst_path, recursive=True)

    def copy_to_backend(self, src_path, dst_path):
        raise NotImplementedError

    def list_uploaded(self, path):
        raise NotImplementedError
