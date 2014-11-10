from optparse import make_option

from django.db.models import Count

from . import InventoryCommand
from inventory.models import Dataset, Distribution


class Command(InventoryCommand):
    help = 'Reports the usage of property values'

    option_list = InventoryCommand.option_list + (
        make_option('--licenses', action='store_true', dest='licenses',
                    default=False,
                    help='Report license usage.'),
        make_option('--media-types', action='store_true', dest='media_types',
                    default=False,
                    help='Report media type usage.'),
    )

    def handle(self, *args, **options):
        self.setup(*args, **options)

        if options['media_types']:
            self.report(Distribution, 'mediaType', distinct='dataset_id')
        if options['licenses']:
            self.report(Dataset, 'license', distinct='id')

    def report(self, klass, field, *, distinct):
        for catalog in self.catalogs:
            count = Dataset.objects.filter(country_code=catalog.country_code).count()
            print('{} ({})'.format(catalog.country_code, count))
            for value in klass.objects.filter(country_code=catalog.country_code).values(field).annotate(count=Count(distinct, distinct=True)).order_by('count'):
                print('  {:7.2%} {} ({})'.format(value['count'] / count, value[field], value['count']))
