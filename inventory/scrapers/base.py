import logging

class Scraper(object):
  def __init__(self, country_code):
      self.country_code = country_code

      self.logger = logging.getLogger('inventory')
      self.info = self.logger.info
      self.debug = self.logger.debug
      self.warning = self.logger.warning
      self.error = self.logger.error
      self.critical = self.logger.critical

  def __str__(self):
    return '%s: %s' % (self.country_code, self.__class__.__name__)

  @classmethod
  def supported_country_codes(cls):
    return sorted(cls.supported_urls().keys())

  @property
  def url(self):
    return self.supported_urls()[self.country_code]

  def scrape(self):
    for package in self.get_packages() or []:
        self.save_package(package)

  def find_or_initialize(self, klass, **options):
    try:
        return klass.objects.get(**options)
    except klass.DoesNotExist:
        return klass(**options)
