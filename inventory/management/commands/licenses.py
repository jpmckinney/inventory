from django.db.models import Count

from .base import InventoryCommand
from inventory.models import Dataset


class Command(InventoryCommand):
    def handle(self, *args, **options):
        for country_code in self.country_codes():
            qs = Dataset.objects.filter(country_code=country_code)
            count = qs.count()
            print(country_code)
            for value in qs.values('license').annotate(count=Count('id', distinct=True)).order_by('count'):
                print('  {:7.2%} {} ({})'.format(value['count'] / count, value['license'], value['count']))
