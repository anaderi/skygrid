from sh import xrdfs, xrdcopy
from .base import BackendBase


class XrootdBackend(BackendBase):
    def __init__(self, xrd_server):
        self.xrd_server = xrd_server

    def copy_from_backend(self, src_path, dst_path):
        xrdcopy("-r", self.xrd_server + src_path, dst_path)

    def copy_to_backend(self, src_path, dst_path):
        xrdfs(self.xrdfs_server, "mkdir", "-p", dst_path)
        xrdcopy("-r", src_path, self.xrd_server + dst_path)

    def list_uploaded(self, path):
        xrdfs(self.xrdfs_server, "ls", path).split("\n")
