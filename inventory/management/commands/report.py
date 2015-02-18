import json
import sys
from collections import defaultdict
from optparse import make_option

import ckanapi
import pandas as pd
import lxml
from django.db.models import Count

from . import InventoryCommand
from inventory.models import Dataset, Distribution


class Command(InventoryCommand):
    help = 'Analyzes catalogs'

    option_list = InventoryCommand.option_list + (
        make_option('--dcat', action='append_const', dest='reports', const='dcat',
                    help='Usage of DCAT by CKAN catalogs.'),
        make_option('--pod', action='append_const', dest='reports', const='pod',
                    help='Usage of Project Open Data Metadata Schema.'),
        make_option('--schemaorg', action='append_const', dest='reports', const='schemaorg',
                    help='Usage of Schema.org.'),
        make_option('--federation', action='append_const', dest='reports', const='federation',
                    help='Usage of Federation technologies.'),
        make_option('--media-types', action='append_const', dest='reports', const='media_types',
                    help='Usage of media types.'),
        make_option('--licenses', action='append_const', dest='reports', const='licenses',
                    help='Usage of licenses.'),
        make_option('--csv', action='store_const', dest='format', const='csv',
                    default='table',
                    help='Prints the results as CSV.'),
    )

    def handle(self, *args, **options):
        self.setup(*args, **options)

        for report in options['reports']:
            result = getattr(self, report)()
            if result is not None:
                if options['format'] == 'table':
                    result.to_string(sys.stdout)
                elif options['format'] == 'csv':
                    result.to_csv(sys.stdout)

    def series(self, getter):
        series = {}
        for catalog in self.catalogs:
            series[catalog.division_id] = getter(catalog)
        return pd.Series(series)

    def dcat(self):
        def getter(catalog):
            if catalog.scraper.__name__ == 'CKAN':
                datasets = Dataset.objects.filter(division_id=catalog.division_id)
                if datasets.exists():
                    response = self.get(catalog.dataset_url(datasets[0]))
                    if response.status_code == 200:
                        response = self.get(catalog.dataset_rdf_url(datasets[0]))
                        return int(response.status_code == 200)

        return self.series(getter)

    def pod(self):
        def getter(catalog):
            response = self.get(catalog.data_json_url)
            return int(response.status_code == 200)

        return self.series(getter)

    def schemaorg(self):
        def getter(catalog):
            datasets = Dataset.objects.filter(division_id=catalog.division_id)
            if datasets.exists():
                url = catalog.dataset_url(datasets[0])
                if url:
                    response = self.get(url)
                    if response.status_code == 200:
                        return int('http://schema.org/Dataset' in response.text)

        return self.series(getter)

    def federation(self):
        frame = defaultdict(lambda: defaultdict(int))
        for catalog in self.catalogs:
            # Assumes we don't need to paginate.
            if catalog.scraper.__name__ == 'CKAN':
                client = ckanapi.RemoteCKAN(catalog.url, get_only=catalog.get_only)
                package_search = client.call_action('package_search', {'fq': 'type:harvest', 'rows': 300000}, verify=catalog.verify)

                if package_search['results']:
                    for package in package_search['results']:
                        source_type = self.source_type(catalog, package)
                        if source_type:
                            frame[source_type][catalog.division_id] += 1
                        else:
                            self.warning('could not determine source type of {}'.format(catalog.dataset_api_url(package)))
                # GB
                else:
                    try:
                        for package in client.call_action('harvest_source_list', verify=catalog.verify):
                            if package['active']:
                                source_type = normalize_source_type(package, package['type'])
                                if source_type:
                                    frame[source_type][catalog.division_id] += 1
                                else:
                                    self.warning('could not determine source type of {}'.format(catalog.harvest_api_url(package)))
                    except ckanapi.errors.CKANAPIError:
                        pass
            elif catalog.scraper.__name__ == 'Socrata':
                if 'federation_filter' in self.get(catalog.url).text:
                    frame['socrata'][catalog.division_id] = 1
        return pd.DataFrame(frame)

    def licenses(self):
        self.report(Dataset, 'license', distinct='id')

    def media_types(self):
        self.report(Distribution, 'mediaType', distinct='dataset_id')

    def report(self, klass, field, *, distinct):
        for catalog in self.catalogs:
            count = Dataset.objects.filter(division_id=catalog.division_id).count()
            print('{} ({})'.format(catalog.division_id, count))
            for value in klass.objects.filter(division_id=catalog.division_id).values(field).annotate(count=Count(distinct, distinct=True)).order_by('count').iterator():
                print('  {:7.2%} {} ({})'.format(value['count'] / count, value[field], value['count']))

    def source_type(self, catalog, package):
        # AU, FI, IE, IT, MX, PY
        if package.get('source_type'):
            return normalize_source_type(package, package['source_type'])

        # IT
        elif '/api/rest/dataset/' in package['url']:
            url, name = package['url'].split('api/rest/dataset/', 1)
            return self.source_type(catalog, ckanapi.RemoteCKAN(url).call_action('package_show', {'id': name}))

        # US
        # @see https://github.com/ckan/ckanext-spatial/blob/master/doc/harvesters.rst
        # @see https://github.com/GSA/ckanext-geodatagov/tree/master/ckanext/geodatagov/harvesters
        elif package.get('extras'):
            source_type = next(extra['value'] for extra in package['extras'] if extra['key'] == 'source_type')
            # @see https://github.com/GSA/ckanext-geodatagov/blob/master/ckanext/geodatagov/harvesters/base.py#L174
            if source_type == 'single-doc':
                response = self.get(package['url'])
                if response.status_code == 200:
                    try:
                        return normalize_scheme(response)
                    except lxml.etree.XMLSyntaxError:
                        pass
            # @see https://github.com/GSA/ckanext-geodatagov/blob/master/ckanext/geodatagov/harvesters/waf_collection.py
            elif source_type == 'waf-collection':
                # @see https://github.com/GSA/ckanext-geodatagov/blob/master/ckanext/geodatagov/validation/__init__.py
                config = json.loads(next(extra['value'] for extra in package['extras'] if extra['key'] == 'config'))
                if config.get('validator_profiles'):
                    if len(config['validator_profiles']) > 1:
                        self.warning('multiple validator_profiles for {}'.format(catalog.dataset_api_url(package)))
                    else:
                        return 'waf-{}'.format(validators[config['validator_profiles'][0]])
                else:
                    response = self.get(config['collection_metadata_url'])
                    if response.status_code == 200:
                        scheme = normalize_scheme(response)
                        if scheme:
                            return 'waf-{}'.format(scheme)
            else:
                normalized = normalize_source_type(package, source_type)
                if normalized:
                    return normalized

        # BR
        else:
            try:
                if ckanapi.RemoteCKAN(package['url']).call_action('site_read'):
                    return 'ckan'
            except ckanapi.errors.CKANAPIError:
                pass


def normalize_source_type(package, source_type):
    if source_type in source_types:
        return source_types[source_type]
    elif package['url'].endswith('/csw') or '/csw/' in package['url']:
        return 'csw'


def normalize_scheme(response):
    if 'FGDC-STD-001-1998' in response.text:
        return 'fgdc'
    elif lxml.etree.fromstring(response.content).xpath('/MD_Metadata|/gmi:MI_Metadata', namespaces={'gmi': 'http://www.isotc211.org/2005/gmi'}):
        return 'iso19139'


source_types = {
    # Dynamic API
    'arcgis': 'arcgis',
    'ckan': 'ckan',
    'csw': 'csw',
    'waf': 'waf',
    # GB
    'gemini-waf': 'waf-gemini',
    # US
    # @see https://github.com/GSA/ckanext-geodatagov/blob/master/ckanext/geodatagov/harvesters/base.py#L185
    'geoportal': 'csw',
    # @see https://github.com/GSA/ckanext-geodatagov/blob/master/ckanext/geodatagov/harvesters/z3950.py
    'z3950': 'iso23950',

    # Static file
    # GB
    'dcat_rdf': 'dcat_rdf',
    'data_json': 'dcat_json',
    'gemini-single': 'gemini',
    'inventory': 'datashare',
    # MX
    'dcat_json': 'pod',  # v1.0
    # US
    'datajson': 'pod',
}

validators = {
    'fgdc_minimal': 'fgdc',
    'iso19139ngdc': 'iso19139',
}
