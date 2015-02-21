import logging
from urllib.parse import urlparse


class Scraper(object):
    def __init__(self, catalog):
        self.catalog = catalog

        self.logger = logging.getLogger('inventory')
        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.exception = self.logger.exception

    def __str__(self):
        return str(self.catalog)

    def scrape(self):
        for package in self.get_packages() or []:
            self.save_package(package)

    def find_or_initialize(self, klass, **options):
        try:
            return klass.objects.get(**options)
        except klass.DoesNotExist:
            return klass(**options)

    def get_packages(self):
        raise NotImplementedError('Please implement this method')

    def save_package(self, package):
        raise NotImplementedError('Please implement this method')
