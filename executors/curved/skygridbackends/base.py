class BackendBase(object):
    def copy_from_backend(self, src_path, dst_path):
        raise NotImplementedError()

    def copy_to_backend(self, src_path, dst_path):
        raise NotImplementedError()

    def list_uploaded(self, path):
        raise NotImplementedError()
