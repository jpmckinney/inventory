import logging

from django.core.management.base import BaseCommand

from inventory.models import Dataset


class InventoryCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(InventoryCommand, self).__init__(*args, **kwargs)

        self.logger = logging.getLogger('inventory')
        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical

    def country_codes(self):
        return Dataset.objects.order_by('country_code').distinct('country_code').values_list('country_code', flat=True)
