import logging

class Scraper(object):
    def __init__(self, catalog):
        self.logger = logging.getLogger('inventory')
        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical

        self.catalog = catalog

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


class Catalog(object):
    def __init__(self, country_code, url, *, scraper, get_only=True, parameters={}):
        self.country_code = country_code
        self.url = url
        self.scraper = scraper
        self.get_only = get_only
        self.parameters = parameters

    def __str__(self):
        return '{}: {}'.format(self.country_code, self.scraper.__name__)
