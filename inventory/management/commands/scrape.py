import logging
import signal
import sys
from multiprocessing import Process
from optparse import make_option

import requests_cache

from . import InventoryCommand


class Command(InventoryCommand):
    args = '<country_code country_code ...>'
    help = 'Scrapes datasets and distributions from data catalog APIs'

    option_list = InventoryCommand.option_list + (
        make_option('--no-cache', action='store_false', dest='cache',
                    default=True,
                    help='Do not cache HTTP GET requests.'),
        make_option('--expire-after', action='store', dest='expire_after',
                    type='int',
                    help='The number of seconds after which the cache is expired.'),
    )

    def handle(self, *args, **options):
        self.setup(*args, **options)

        for catalog in self.catalogs:
            print(catalog)

        if options['dry_run']:
            exit(0)

        # @see http://requests-cache.readthedocs.org/en/latest/api.html#requests_cache.core.install_cache
        if options['cache']:
            cache_options = {}
            if options['expire_after']:
                cache_options['expire_after'] = options['expire_after']
            requests_cache.install_cache('inventory_cache', allowable_methods=('HEAD', 'GET', 'POST'), **cache_options)

        processes = [
            Process(target=self.scrape, args=(catalog,))
            for catalog in self.catalogs
        ]

        def signal_handler(signal, frame):
            for process in processes:
                process.terminate()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        for process in processes:
            process.start()

        for process in processes:
            process.join()

    def scrape(self, catalog):
        catalog.scraper(catalog).scrape()
        self.info('{} done'.format(catalog))
