import json
import os
import subprocess
from contextlib import closing
from optparse import make_option
from urllib.parse import quote

import requests

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
        url = quote(distribution.accessURL, safe="%/:=&?~#+!$,;'@()*[]") # @todo where are these characters from?

        # @see http://docs.python-requests.org/en/latest/user/advanced/#body-content-workflow
        with closing(requests.get(url, stream=True, allow_redirects=False)) as response:
            distribution.validation_encoding = response.encoding or ''
            distribution.validation_content_type = response.headers.get('content-type', '')
            distribution.validation_headers = dict(response.headers)

            if response.status_code == 200:
                content_length = int(response.headers.get('content-length', 0))
                human_size = format_size(int(content_length))
                if content_length < 1e6:  # 1MB
                    self.info('{} {}'.format(human_size, url))

                    (success, data) = self.validate_csv(url)

                    if success:
                        distribution.valid = data['valid']
                        distribution.validation_encoding = data['encoding']
                        distribution.validation_content_type = data['content_type']
                        distribution.validation_headers = data['headers']
                        distribution.validation_errors = data['errors']
                        distribution.save()

                        if data['errors']:
                            self.debug(data['errors'])
                    else:
                        self.error(data)
                else:
                    self.warning('too large {} {}'.format(human_size, url))
                    distribution.valid = False
                    distribution.validation_errors = ['too_large']
                    distribution.save()
            else:
                self.warning('HTTP {} code {}'.format(response.status_code, url))
                distribution.valid = False
                distribution.validation_errors = ['http_{}'.format(response.status_code)]
                distribution.save()

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


def format_size(number, suffix='B'):
    for unit in ['', 'K', 'M', 'G']:
        if number < 1000:
            return '%3.1f %s%s' % (number, unit, suffix)
        number /= 1000
    return '%.1f %s%s' % (number, 'T', suffix)
