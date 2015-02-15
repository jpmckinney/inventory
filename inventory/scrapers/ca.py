import json

from .ckan import CKAN


class CA(CKAN):
    # The stream regularly fails with "transfer closed with X bytes remaining to
    # read". We therefore download the file with `wget` and parse locally.
    def get_packages(self):
        with open('od-do-canada.jl') as f:
            for line in f:
                print('.', end='', flush=True)
                self.save_package(json.loads(line))

    """
    import zlib

    import pycurl

    def scrape(self):
        # We can't yield from inside PycURL's WRITEFUNCTION.
        self.get_packages()

    def get_packages(self):
        # @see http://www.zlib.net/manual.html#inflateInit2
        self.decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
        self.buf = ''

        client = pycurl.Curl()
        # @see http://open.canada.ca/data/en/dataset/c4c5c7f1-bfa6-4ff6-b4a0-c164cb2060f7
        client.setopt(pycurl.URL, 'http://open.canada.ca/static/od-do-canada.jl.gz')
        client.setopt(pycurl.WRITEFUNCTION, self.write)
        client.perform()

    def write(self, data):
        self.buf += self.decompressor.decompress(data).decode('utf-8')
        if self.buf.find('\n') >= 0:
            *lines, self.buf = self.buf.split('\n')
            for line in lines:
                print('.', end='', flush=True)
                self.save_package(json.loads(line))
    """
