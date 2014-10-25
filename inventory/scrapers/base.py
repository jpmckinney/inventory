import logging

class Scraper(object):
  def __init__(self, country_code, url):
      self.country_code = country_code
      self.url = url

      self.logger = logging.getLogger('inventory')
      self.info = self.logger.info
      self.debug = self.logger.debug
      self.warning = self.logger.warning
      self.error = self.logger.error
      self.critical = self.logger.critical

  def scrape(self):
    for package in self.get_packages() or []:
        self.save_package(package)

  def find_or_initialize(self, klass, **options):
    try:
        return klass.objects.get(**options)
    except klass.DoesNotExist:
        return klass(**options)
