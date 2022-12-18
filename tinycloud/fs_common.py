from exceptions import UnsupportedOporation


class Fs:
    def isdir(self, path):
        raise UnsupportedOporation

    def list(self, path="/"):
        raise UnsupportedOporation

    def prop(self, path):
        raise UnsupportedOporation

    def read(self, path, chunk_size="1M"):
        raise UnsupportedOporation

    def write(self, path, stream, chunk_size="1M"):
        raise UnsupportedOporation

    def delete(self, path):
        raise UnsupportedOporation

    def mkdir(self, path):
        raise UnsupportedOporation
