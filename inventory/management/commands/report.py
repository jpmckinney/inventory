import csv
import itertools
from optparse import make_option

import requests
from django.db.models import Count
from urllib.parse import urlparse

from . import InventoryCommand
from inventory.models import Dataset, Distribution


class Command(InventoryCommand):
    help = 'Reports the usage of property values'

    option_list = InventoryCommand.option_list + (
        make_option('--dcat', action='store_true', dest='dcat',
                    default=False,
                    help='Report DCAT usage by CKAN catalogs.'),
        make_option('--pod', action='store_true', dest='pod',
                    default=False,
                    help='Report Project Open Data Metadata Schema usage.'),
        make_option('--schemaorg', action='store_true', dest='schemaorg',
                    default=False,
                    help='Report Schema.org usage.'),
        make_option('--licenses', action='store_true', dest='licenses',
                    default=False,
                    help='Report license usage.'),
        make_option('--media-types', action='store_true', dest='media_types',
                    default=False,
                    help='Report media type usage.'),
        make_option('--structures', action='store_true', dest='structures',
                    default=False,
                    help='Report catalog structures.'),
    )

    def handle(self, *args, **options):
        self.setup(*args, **options)

        if options['media_types']:
            self.report(Distribution, 'mediaType', distinct='dataset_id')
        if options['licenses']:
            self.report(Dataset, 'license', distinct='id')

        if options['dcat']:
            for catalog in self.catalogs:
                if catalog.scraper.__name__ == 'CKAN':
                    datasets = Dataset.objects.filter(division_id=catalog.division_id)
                    if datasets:
                        url = '{}dataset/{}'.format(catalog.url, datasets[0].name)
                        response = requests.get(url, verify=False)
                        if response.status_code == 200:
                            url = '{}.rdf'.format(url)
                            response = requests.get(url, verify=False)
                        print('{} {}'.format(response.status_code, url))
        if options['pod']:
            for catalog in self.catalogs:
                parsed = urlparse(catalog.url)
                url = '{}://{}/data.json'.format(parsed.scheme, parsed.netloc)
                response = requests.get(url, verify=False)
                print('{} {}'.format(response.status_code, url))
        if options['schemaorg']:
            for catalog in self.catalogs:
                datasets = Dataset.objects.filter(division_id=catalog.division_id)
                if datasets:
                    if catalog.scraper.__name__ == 'CKAN':
                        url = '{}dataset/{}'.format(catalog.url, datasets[0].name)
                    elif catalog.scraper.__name__ == 'OpenColibri':
                        url = '{}dataset/{}'.format(catalog.url, datasets[0].identifier)
                    elif catalog.scraper.__name__ == 'RDF':
                        url = datasets[0].name
                    else:
                        url = datasets[0].landingPage
                    if url:
                        response = requests.get(url, verify=False)
                        if response.status_code == 200:
                            if 'http://schema.org/Dataset' in response.text:
                                print('yes {} {}'.format(url, catalog.scraper.__name__))
                            else:
                                print('no  {} {}'.format(url, catalog.scraper.__name__))
                        else:
                            print('{} {}'.format(response.status_code, url))
                    else:
                        print('missing dataset url for {}'.format(catalog.division_id))

        if options['structures']:
            columns = []
            for catalog in self.catalogs:
                datasets = Dataset.objects.filter(division_id=catalog.division_id)
                distributions = Distribution.objects.filter(division_id=catalog.division_id)
                counts = datasets.values('id').annotate(count=Count('distribution'))
                columns.append(counts.values_list('count', flat=True))
                if datasets.count():
                    print('{}\t{:6d}\t{:6d}\t{:7.2%}\t{:7.2%}\t{:7.2%}'.format(
                        catalog.division_id,
                        datasets.count(),
                        distributions.count(),
                        counts.filter(count=0).count() / datasets.count(),
                        counts.filter(count=1).count() / datasets.count(),
                        counts.filter(count__gt=1).count() / datasets.count(),
                    ))


            with open('structures.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow([catalog.division_id for catalog in self.catalogs])
                for row in itertools.zip_longest(*columns):
                    writer.writerow(row)


    def report(self, klass, field, *, distinct):
        for catalog in self.catalogs:
            count = Dataset.objects.filter(division_id=catalog.division_id).count()
            print('{} ({})'.format(catalog.division_id, count))
            for value in klass.objects.filter(division_id=catalog.division_id).values(field).annotate(count=Count(distinct, distinct=True)).order_by('count'):
                print('  {:7.2%} {} ({})'.format(value['count'] / count, value[field], value['count']))
