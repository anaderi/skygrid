import os
import shutil
import errno

from .base import BackendBase


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

        self.mkdir_p(dst_path)

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

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise
