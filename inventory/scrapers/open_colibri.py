import requests

from .base import Scraper
from ..models import Dataset, Distribution

class OpenColibri(Scraper):
    # http://data.gov.gr/api/public/v1/datasets/?format=json has "country" as an
    # object instead of as a string, adds "maintainingGroup", properly expands
    # "categories", but lacks "resources".
    def get_packages(self):
        try:
            packages = requests.get(self.catalog.url + 'api/public/v1/datasetsapi/?format=json&limit=1000').json()['objects']
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %s' % self.catalog.url)
            return

        self.info('%d packages %s' % (len(packages), self.catalog.url))

        for package in packages:
            yield package

    def save_package(self, package):
        source_url = '%sapi/public/v1/datasetsapi/%s/' % (self.catalog.url, package['id'])

        dataset = self.find_or_initialize(Dataset, division_id=self.catalog.division_id, name=package['id'])
        dataset.json = package
        dataset.custom_properties = [key for key, value in package.items() if value and key not in opencolibri_dataset_properties]
        dataset.source_url = source_url
        for dataset_property, column_name in dataset_properties.items():
            if package.get(dataset_property) is not None:
                setattr(dataset, column_name, package[dataset_property])

        dataset.save()

        for resource in package.get('distribution', []):
            distribution = self.find_or_initialize(Distribution, dataset=dataset, _id=resource['id'])
            distribution.json = resource
            distribution.custom_properties = [key for key, value in resource.items() if value and key not in opencolibri_distribution_properties]
            distribution.division_id = dataset.division_id
            for distribution_property, column_name in distribution_properties.items():
                if resource.get(distribution_property) is not None:
                    setattr(distribution, column_name, resource[distribution_property])
                if resource.get('file'):
                    distribution.accessURL = resource['file']
                elif resource.get('uri'):
                    distribution.accessURL = resource['uri']
                if resource.get('file') and resource.get('uri'):
                    self.warning("both file and uri are set %s" % source_url)


            distribution.save()

opencolibri_dataset_properties = frozenset([
    'author',
    'categories',
    'country',
    'created_date',
    'date_published',  # blank
    'description',
    'descriptionen',
    'id',
    'license',
    'modified_date',
    'publisher',
    'rating_score',
    'rating_votes',
    'resource_uri',
    'resources',
    'state',
    'title',
    'titleen',
    'uploader',
    'url',
    'views',
])
opencolibri_distribution_properties = frozenset([
    'created_date',
    'description',
    'downloads',
    'file',
    'format',
    'id',
    'jsonfile',
    'language',  # dct:language
    'modified_date',
    'resource_uri',
    'uri',
])

dataset_properties = {
    'titleen': 'title',
    'descriptionen': 'description',
    'created_date': 'issued',
    'modified_date': 'modified',
    'publisher': 'publisher',
    'id': 'identifier',
    'url': 'landingPage',
    'license': 'license_id',
}

distribution_properties = {
    'description': 'description',
    'created_date': 'issued',
    'modified_date': 'modified',
    'format': 'format',
}
