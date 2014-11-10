import logging
import sys
from optparse import make_option

from django.core.management.base import BaseCommand
from logutils.colorize import ColorizingStreamHandler

from inventory.models import Dataset
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
    args = '<country_code country_code ...>'

    option_list = BaseCommand.option_list + (
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

        self.catalogs = []
        for catalog in catalogs:
            if not args or catalog.country_code in args and not options['exclude'] or catalog.country_code not in args and options['exclude']:
                self.catalogs.append(catalog)
