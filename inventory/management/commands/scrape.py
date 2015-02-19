from . import InventoryCommand


class Command(InventoryCommand):
    args = '<identifier identifier ...>'
    help = 'Scrapes datasets and distributions from catalogs'

    def handle(self, *args, **options):
        self.setup(*args, **options)
        self.multiprocess(self.scrape, {'dry_run': options['dry_run']})

    def scrape(self, catalog, *, dry_run=False):
        if not dry_run:
            catalog.scraper(catalog).scrape()
        self.info('{} done'.format(catalog))
