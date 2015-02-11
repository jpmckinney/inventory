import re

import requests

from .base import Scraper
from ..models import Dataset, Distribution

citation_re = re.compile(r'\b(?:citation|mu[cs]t (?:acknowledge|cite|be attributed))\b')
python_value_re = re.compile(r"\A\[u'")
gb_open_license_re = re.compile(r'open government licen[sc]e', re.IGNORECASE)


class Socrata(Scraper):
    def get_packages(self):
        try:
            packages = requests.get(self.catalog.url + 'data.json').json()['dataset']
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %s' % self.catalog.url)
            return

        self.info('%d packages %s' % (len(packages), self.catalog.url))

        for package in packages:
            yield package

    def save_package(self, package):
        source_url = '%s#%s' % (self.catalog.url, package['identifier'])

        dataset = self.find_or_initialize(Dataset, division_id=self.catalog.division_id, name=package['identifier'])
        dataset.json = package
        dataset.custom_properties = [key for key, value in package.items() if value and key not in socrata_dataset_properties]
        dataset.source_url = source_url
        for dataset_property, column_name in dataset_properties.items():
            if package.get(dataset_property) is not None:
                setattr(dataset, column_name, package[dataset_property])
        if package['contactPoint']['fn'] != '<Nobody>' and package['contactPoint']['hasEmail'] != 'mailto:':
            dataset.maintainer = package['contactPoint']['fn']
            dataset.maintainer_email = package['contactPoint']['hasEmail']
        dataset.publisher = package['publisher']['name']

        dataset.save()

        for resource in package.get('distribution', []):
            distribution = self.find_or_initialize(Distribution, dataset=dataset, _id='%s#%s' % (package['identifier'], resource['mediaType']))
            distribution.json = resource
            distribution.custom_properties = [key for key, value in resource.items() if value and key not in socrata_distribution_properties]
            distribution.division_id = dataset.division_id
            for distribution_property, column_name in distribution_properties.items():
                if resource.get(distribution_property) is not None:
                    setattr(distribution, column_name, resource[distribution_property])

            distribution.save()


socrata_dataset_properties = frozenset([
    'accessLevel',
    'contactPoint',
    'description',
    'distribution',
    'identifier',
    'issued',
    'keyword',
    'landingPage',
    'license',
    'modified',
    'publisher',
    'theme',
    'title',
])
socrata_distribution_properties = frozenset([
    'downloadURL',
    'mediaType',
])

dataset_properties = {
    'accessLevel': 'accessLevel',
    'description': 'description',
    'identifier': 'identifier',
    'issued': 'issued',
    'keyword': 'keyword',
    'landingPage': 'landingPage',
    'license': 'license_id',
    'modified': 'modified',
    'theme': 'theme',
    'title': 'title',
}
distribution_properties = {
    'accessURL': 'downloadURL',
    'mediaType': 'mediaType',
}
