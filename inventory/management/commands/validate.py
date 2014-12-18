# @todo code review
import json
import logging
import signal
import sys
import os
from urllib.parse import quote
import requests

from optparse import make_option
from Naked.toolshed.shell import muterun_rb
from . import InventoryCommand
from inventory.models import Dataset, Distribution
from django.core.management.base import BaseCommand
from logutils.colorize import ColorizingStreamHandler
from inventory.scrapers import catalogs

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
                    help='Specifies the number of distributions (e.g files) to validate in this batch (per country is country codes are provided.'),
        make_option('--nb-lines', action='store', dest='nb_lines',
                    default=0,
                    help='For each CSV files, limit the maximum number of lines to evaluate (e.g runs faster.'),
    )

    def handle(self, *args, **options):
        
        
        self.warnings = 0
        self.options = options

        logger.setLevel(logging.DEBUG)
        handler = Handler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(levelname)-5s %(asctime)s %(message)s', datefmt='%H:%M:%S'))

        self.setup(*args, **options)
        self.ruby_path = os.getcwd() + '/inventory/validators/csv/validate_csv.rb'

        for catalog in self.catalogs:
            qs = Distribution.objects.filter(mediaType='text/csv'
                ).filter(valid__isnull=True
                ).filter(country_code=catalog.country_code)

            if self.options["nb_distribution"] != 0:

                qs = qs[0:int(self.options["nb_distribution"])]

            for distribution in qs:
                self.execute_validation(distribution)



    def execute_validation(self, distribution):

        url = quote(distribution.accessURL, safe="%/:=&?~#+!$,;'@()*[]")

        try:
            r = requests.get(url, stream=True)
            if r is not None and 'content-length'  in r.headers and int(r.headers['content-length']) > 1000000000:
                logger.info('File  %s is too large (%s), skipping it' % (url, r.headers['content-length']))
                distribution.validation_headers = r.headers
                distribution.valid = False
                distribution.validation_errors = ["too_large"]
                distribution.save()
            else:

                logger.info('Validating %s' % url)

                (result, data) = self.csv_validator(url, self.options["nb_lines"])

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
        except :
           distribution.validation_headers = ''
           distribution.valid = False
           distribution.validation_errors = ["not_found"]
           distribution.save()



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

