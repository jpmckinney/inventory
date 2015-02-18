import json
import os
import subprocess
from optparse import make_option
from urllib.parse import quote

from . import InventoryCommand, number_to_human_size
from inventory.models import Distribution


class Command(InventoryCommand):
    args = '<identifier identifier ...>'
    help = 'Validates CSV files with CSVLint.rb (must run headers command first)'

    csv_validator_path = os.path.join(os.getcwd(), 'inventory', 'validators', 'csv', 'validate_csv.rb')

    option_list = InventoryCommand.option_list + (
        make_option('--distributions', type='int', action='store', dest='distributions',
                    default=0,
                    help='The number of CSV files to validate per catalog.'),
        make_option('--rows', type='int', action='store', dest='rows',
                    default=0,
                    help='The number of CSV rows to process per file.'),
    )

    def handle(self, *args, **options):
        self.setup(*args, **options)
        self.options = options

        for catalog in self.catalogs:
            distributions = Distribution.objects.filter(division_id=catalog.division_id, mediaType='text/csv', valid__isnull=True)

            if self.options['distributions']:
                distributions = distributions[:self.options['distributions']]

            for distribution in distributions.iterator():
                self.validate(distribution)

    def validate(self, distribution):
        if distribution.http_status_code == 200 and distribution.http_content_length and distribution.http_content_length < 1e6:  # 1 MB
            # @see http://stackoverflow.com/a/845595/244258
            url = quote(distribution.accessURL, safe="%/:=&?~#+!$,;'@()*[]")
            self.info('{} {}'.format(number_to_human_size(distribution.http_content_length), url))
            (success, data) = self.validate_csv(url)

            if success:
                distribution.valid = data['valid']
                distribution.errors = data['errors']
                distribution.save()
                if data['errors']:
                    self.debug(data['errors'])
            else:
                self.error(data)

    # @see https://github.com/theodi/csvlint.rb#errors
    def validate_csv(self, url):
        args = ['ruby', self.csv_validator_path, url]

        if self.options['rows']:
            args.append(str(self.options['rows']))

        try:
            output = subprocess.check_output(args)
        except subprocess.CalledProcessError as err:
            return (False, err.output.decode('utf-8'))

        return (True, json.loads(output.decode('utf-8')))
