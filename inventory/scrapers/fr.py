import requests

from .base import Scraper
from ..models import Dataset, Distribution


class FR(Scraper):
    def get_packages(self):
        try:
            response = requests.get(self.catalog.url + 'api/1/datasets/?page_size=500').json()  # > 750 causes 500 errors
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %s' % self.catalog.url)
            return

        self.info('%d packages %s' % (response['total'], self.catalog.url))

        for package in response['data']:
            yield package

        while response['next_page']:
            try:
                response = requests.get(response['next_page']).json()

                for package in response['data']:
                    yield package
            except requests.packages.urllib3.exceptions.ProtocolError:
                self.error('ProtocolError %s' % self.catalog.url)
                return

    def save_package(self, package):
        # @todo continue
        pass
