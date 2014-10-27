import logging
import signal
import sys
from multiprocessing import Process
from optparse import make_option

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

logger = logging.getLogger()  # 'inventory' to quiet requests


class Command(BaseCommand):
    args = '<country_code country_code ...>'
    help = 'Scrapes datasets and distributions from data catalog APIs'

    option_list = BaseCommand.option_list + (
        make_option('--no-cache', action='store_false', dest='cache',
                    default=True,
                    help='Do not cache HTTP GET requests.'),
        make_option('--expire-after', action='store', dest='expire_after',
                    type='int',
                    help='The number of seconds after which the cache is expired.'),
        make_option('--exclude', action='store_true', dest='exclude',
                    default=False,
                    help='Exclude the given country codes.'),
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

    def handle(self, *args, **options):
        # @see http://requests-cache.readthedocs.org/en/latest/api.html#requests_cache.core.install_cache
        if options['cache']:
            cache_options = {}
            if options['expire_after']:
                cache_options['expire_after'] = options['expire_after']
            requests_cache.install_cache('inventory_cache', allowable_methods=('HEAD', 'GET', 'POST'), **cache_options)

        logger.setLevel(options['level'] or logging.DEBUG)
        handler = Handler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(levelname)-5s %(asctime)s %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(handler)

        scrapers = []
        for catalog in catalogs:
            if not args or catalog.country_code in args and not options['exclude'] or catalog.country_code not in args and options['exclude']:
                scraper = catalog.scraper(catalog)
                scrapers.append(scraper)
                print(scraper)

        if options['dry_run']:
            exit(0)

        processes = [
            Process(target=self.scrape, args=(scraper,))
            for scraper in scrapers
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

    def scrape(self, scraper):
        scraper.scrape()
        logger.info('{} done'.format(scraper))
