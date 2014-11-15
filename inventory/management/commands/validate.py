# @todo code review
import json
import logging
import signal
import sys
import os

from optparse import make_option
from Naked.toolshed.shell import muterun_rb
from . import InventoryCommand
from inventory.models import Dataset, Distribution
from django.core.management.base import BaseCommand
from logutils.colorize import ColorizingStreamHandler

class Handler(ColorizingStreamHandler):
    level_map = {
        logging.DEBUG: (None, 'cyan', False),
        logging.INFO: (None, 'white', False),
        logging.WARNING: (None, 'yellow', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', True),
    }

logger = logging.getLogger()  # 'inventory' to quiet requests



class Command(InventoryCommand):

    args = '<country_code country_code ...>'
    help = 'Validate files formats'

    option_list = InventoryCommand.option_list + (
        make_option('--nb-distribution', action='store', dest='nb_distribution',
                    default=0,
                    help='Specifies the number of distributions (e.g files) to validate in this batch.'),
        make_option('--nb-lines', action='store', dest='nb_lines',
                    default=0,
                    help='For each CSV files, limit the maximum number of lines to evaluate (e.g runs faster.'),
    )

    def handle(self, *args, **options):
        self.warnings = 0

        logger.setLevel(logging.DEBUG)
        handler = Handler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(levelname)-5s %(asctime)s %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(handler)        

        self.ruby_path = os.getcwd() + '/inventory/validators/csv/validate_csv.rb'

        qs = Distribution.objects.filter(format='CSV').filter(valid__isnull=True)

        if options["nb_distribution"] != 0:
            qs = qs[0:int(options["nb_distribution"])]

        for distribution in qs:

            url = distribution.accessURL

            logger.info('Validating %s' % url)

            (result, data) = self.csv_validator(url, options["nb_lines"])

            if result == True:
                distribution.valid = data["valid"]
                distribution.validation_errors = data["errors"]
                distribution.validation_content_type = data["content_type"]
                distribution.validation_encoding = data["encoding"]
                distribution.validation_headers = json.dumps(data["headers"])
                distribution.validation_extension = data["extension"]
                distribution.save()

            else:
                logger.error('Error: %s' % data)


    def csv_validator(self,url, nb_lines):
        
        #TODO - Relative path does not work... will have to find a better way than full path
        command_line = '"' + url + '"'


        if nb_lines != 0:
            command_line += ' ' + nb_lines

        response = muterun_rb(self.ruby_path, command_line)


        if response.exitcode == 0:
          json_content = response.stdout.decode("utf-8")
          data = json.loads(json_content)

          return (True,  data)

        else:
          return (False,  response.stderr.decode("utf-8"))

