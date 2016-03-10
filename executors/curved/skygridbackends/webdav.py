import os
import easywebdav
import errno
from .base import BackendBase


class WebDAVBackend(BackendBase):
    def __init__(self, host, params):
        self.wc = easywebdav.connect(host, **params)

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    def copy_from_backend(self, src_path, dst_path):
        filelist = self.wc.ls(src_path)
        if len(filelist) == 1:
            if os.path.isdir(dst_path):
                basename = src_path.split("/")[-1]
                dst_path = os.path.join(dst_path, basename)

            self.wc.download(src_path, dst_path) # single file, download it

        else:
            # Directory, should go recursively
            directory = filelist[0].name
            directory = directory.split("/")[-2] if directory.endswith("/") else directory.split("/")[-1]
            local_dir_path = os.path.join(dst_path, directory)
            self.mkdir_p(local_dir_path)

            filelist = filelist[1:]
            for f in filelist:
                self.copy_from_backend(f.name, local_dir_path)



    def copy_to_backend(self, src_path, dst_path):
        assert os.path.exists(src_path)

        self.wc.mkdirs(dst_path)

        for root, dirs, files in os.walk(src_path):
            path_in_root = root.replace(src_path, "")
            if path_in_root.startswith('/'):
                path_in_root = path_in_root[1:]

            dst_root = os.path.join(dst_path, path_in_root)
            self.wc.mkdirs(dst_root)

            for basename in files:
                filename = os.path.join(root, basename)

                self.wc.upload(filename, os.path.join(dst_root, basename))


    def list_uploaded(self, path):
        return [f.name for f in self.wc.ls(path)]
