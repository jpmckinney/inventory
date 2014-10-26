from django.core.management.base import BaseCommand

from inventory.models import Dataset


class InventoryCommand(BaseCommand):
    def country_codes(self):
        return Dataset.objects.order_by('country_code').distinct('country_code').values_list('country_code', flat=True)
