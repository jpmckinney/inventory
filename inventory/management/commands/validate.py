import json
import os
from contextlib import closing
from optparse import make_option
from urllib.parse import quote

import requests
from Naked.toolshed.shell import muterun_rb

from . import InventoryCommand
from inventory.models import Distribution


class Command(InventoryCommand):
    args = '<identifier identifier ...>'
    help = 'Validates CSV files with CSVLint.rb'

    csv_validator_path = os.path.join(os.getcwd(), 'inventory', 'validators', 'csv', 'validate_csv.rb')

    option_list = InventoryCommand.option_list + (
        make_option('--distributions', type='int', action='store', dest='distributions',
                    default=0,
                    help='The number of CSV files to validate per catalog'),
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

            for distribution in distributions:
                self.validate(distribution)

    def validate(self, distribution):
        url = quote(distribution.accessURL, safe="%/:=&?~#+!$,;'@()*[]") # @todo

        # @see http://docs.python-requests.org/en/latest/user/advanced/#body-content-workflow
        with closing(requests.get(url, stream=True)) as response:
            if response.status_code == 200:
                if int(response.headers['content-length']) < 100000000:  # 100MB
                    self.info('Validating {}'.format(url))

                    (success, data) = self.validate_csv(url)

                    if success:
                        distribution.valid = data['valid']
                        distribution.validation_encoding = data['encoding']
                        distribution.validation_content_type = data['content_type']
                        distribution.validation_extension = data['extension']
                        distribution.validation_headers = data['headers']
                        distribution.validation_errors = data['errors']
                        distribution.save()

                        if data['errors']:
                            self.debug(data['errors'])
                    else:
                        self.error(data)
                else:
                    self.info('File {} is too large ({}), skipping it'.format(url, response.headers['content-length']))
                    distribution.valid = False
                    distribution.validation_errors = ['too_large']
                    distribution.save()
            else:
                distribution.valid = False
                distribution.validation_errors = ['http_{}'.format(response.status_code)]
                distribution.save()

    # @see https://github.com/theodi/csvlint.rb#errors
    def validate_csv(self, url):
        args = ['"{}"'.format(url)]

        if self.options['rows']:
            args.append(str(self.options['rows']))

        response = muterun_rb(self.csv_validator_path, ' '.join(args))

        if response.exitcode == 0:
            return (True, json.loads(response.stdout.decode('utf-8')))
        else:
            return (False, response.stderr.decode('utf-8'))
