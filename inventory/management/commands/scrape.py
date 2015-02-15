import logging
import signal
import sys
from multiprocessing import Process
from optparse import make_option

from . import InventoryCommand


class Command(InventoryCommand):
    args = '<identifier identifier ...>'
    help = 'Scrapes datasets and distributions from catalogs'

    def handle(self, *args, **options):
        self.setup(*args, **options)

        processes = [
            Process(target=self.scrape, args=(catalog,), kwargs={'dry_run': options['dry_run']})
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

    def scrape(self, catalog, *, dry_run=False):
        if not dry_run:
            catalog.scraper(catalog).scrape()
        self.info('{} done'.format(catalog))
