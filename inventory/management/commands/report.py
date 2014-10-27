from optparse import make_option

from django.db.models import Count

from . import InventoryCommand
from inventory.models import Dataset, Distribution


class Command(InventoryCommand):
    option_list = InventoryCommand.option_list + (
        make_option('--licenses', action='store_true', dest='licenses',
                    default=False,
                    help='Report license usage.'),
        make_option('--media-types', action='store_true', dest='media_types',
                    default=False,
                    help='Report media type usage.'),
    )

    def handle(self, *args, **options):
        if options['media_types']:
            self.report(Distribution, 'mediaType', distinct='dataset_id')
        if options['licenses']:
            self.report(Dataset, 'license', distinct='id')

    def report(self, klass, field, *, distinct):
        for country_code in self.country_codes():
            count = Dataset.objects.filter(country_code=country_code).count()
            print(country_code)
            for value in klass.objects.filter(country_code=country_code).values(field).annotate(count=Count(distinct, distinct=True)).order_by('count'):
                print('  {:7.2%} {} ({})'.format(value['count'] / count, value[field], value['count']))
