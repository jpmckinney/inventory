# coding: utf-8

import logging
import signal
import sys
from multiprocessing import Process
from optparse import make_option

import requests_cache
from django.core.management.base import BaseCommand
from logutils.colorize import ColorizingStreamHandler

from inventory.scrapers import CKANScraper


class Handler(ColorizingStreamHandler):
    level_map = {
        logging.DEBUG: (None, 'cyan', False),
        logging.INFO: (None, 'white', False),
        logging.WARNING: (None, 'yellow', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', True),
    }

logger = logging.getLogger()  # __name__ to quiet requests

# @todo This list must be continually updated.
ckan_urls = frozenset([
    ('ar', 'http://datospublicos.gob.ar/data/'),
    ('au', 'http://data.gov.au/'),
    ('br', 'http://dados.gov.br/'),
    ('ca', 'http://data.gc.ca/data/en/'),
    ('fr', 'http://data.gouv.fr/'),
    ('gb', 'http://data.gov.uk/'),
    ('id', 'http://data.id/'),
    ('ie', 'http://data.gov.ie/'),
    ('it', 'http://www.dati.gov.it/catalog/'),
    ('md', 'http://data.gov.md/ckan'),
    ('mx', 'http://catalogo.datos.gob.mx/'),
    ('nl', 'https://data.overheid.nl/data/'),
    ('ph', 'http://data.gov.ph/catalogue/'),
    ('py', 'http://datos.gov.py/'),
    ('ro', 'http://data.gov.ro/'),
    ('se', 'http://oppnadata.se/'),
    ('sk', 'http://data.gov.sk/'),
    ('tz', 'http://opendata.go.tz/'),
    ('us', 'http://catalog.data.gov/'),
    ('uy', 'https://catalogodatos.gub.uy/'),
    # CKAN is hidden:
    # ('no', 'http://data.norge.no/'),
])


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

        if not args or options['exclude']:
            include = dict(ckan_urls)
        else:
            include = {}

        if args:
            if options['exclude']:
                for arg in args:
                    del include[arg]
            else:
                for country_code, url in ckan_urls:
                    if country_code in args:
                        include[country_code] = url

        for country_code, url in include.items():
            print('{}: {}'.format(country_code, url))

        if options['dry_run']:
            exit(0)

        processes = [
            Process(target=self.scrape, args=(country_code, url))
            for country_code, url in include.items()
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

    def scrape(self, country_code, url):
        CKANScraper(country_code, url).scrape()
        logger.info('%s done' % country_code)
