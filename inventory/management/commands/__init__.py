import logging
import sys
from optparse import make_option

import requests
import requests_cache
from django.core.management.base import BaseCommand
from logutils.colorize import ColorizingStreamHandler

from inventory.scrapers import catalogs


class Handler(ColorizingStreamHandler):
    level_map = {
        logging.DEBUG: (None, 'cyan', False),
        logging.INFO: (None, 'white', False),
        logging.WARNING: (None, 'yellow', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', True),
    }


class InventoryCommand(BaseCommand):
    args = '<identifier identifier ...>'

    option_list = BaseCommand.option_list + (
        make_option('--exclude', action='store_true', dest='exclude',
                    default=False,
                    help='Exclude the given country codes.'),
        make_option('--no-cache', action='store_false', dest='cache',
                    default=True,
                    help='Do not cache HTTP GET requests.'),
        make_option('--expire-after', action='store', dest='expire_after',
                    type='int',
                    help='The number of seconds after which the cache is expired.'),
        make_option('-n', '--dry-run', action='store_true', dest='dry_run',
                    default=False,
                    help='Print the plan without scraping.'),
        make_option('-q', '--quiet', action='store_const', dest='level',
                    const=logging.INFO,
                    help='Quiet mode. No DEBUG messages.'),
        make_option('--silent', action='store_const', dest='level',
                    const=logging.WARNING,
                    help='Quiet mode. No DEBUG or INFO messages.'),
    )

    def __init__(self, *args, **kwargs):
        super(InventoryCommand, self).__init__(*args, **kwargs)

        self.logger = logging.getLogger()  # 'inventory' to quiet requests
        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical

        handler = Handler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(levelname)-5s %(asctime)s %(message)s', datefmt='%H:%M:%S'))
        self.logger.addHandler(handler)

    def setup(self, *args, **options):
        self.logger.setLevel(options['level'] or logging.DEBUG)

        args = ['ocd-division/country:{}'.format(arg) for arg in args]

        self.catalogs = []
        for catalog in catalogs:
            if not args or catalog.division_id in args and not options['exclude'] or catalog.division_id not in args and options['exclude']:
                self.catalogs.append(catalog)

        # @see http://requests-cache.readthedocs.org/en/latest/api.html#requests_cache.core.install_cache
        if options['cache']:
            cache_options = {}
            if options['expire_after']:
                cache_options['expire_after'] = options['expire_after']
            requests_cache.install_cache('inventory_cache', allowable_methods=('HEAD', 'GET', 'POST'), **cache_options)

    def get(self, url):
        try:
            response = requests.get(url)
        except requests.exceptions.SSLError:
            response = requests.get(url, verify=False)
        if response.status_code != 200:
            self.warning('{} {}'.format(response.status_code, response.url))
        return response
