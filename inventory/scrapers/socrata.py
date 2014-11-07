import re

import requests

from .base import Scraper
from ..models import Dataset, Distribution

citation_re = re.compile(r'\b(?:citation|mu[cs]t (?:acknowledge|cite|be attributed))\b')
python_value_re = re.compile(r"\A\[u'")
gb_open_license_re = re.compile(r'open government licen[sc]e', re.IGNORECASE)


class Socrata(Scraper):
    def get_packages(self):
        # Get all the packages.
        try:
            packages = requests.get(self.catalog.url + 'data.json').json()
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %s' % self.catalog.url)
            return

        # Report the total number of packages.
        self.info('%d packages %s' % (len(packages), self.catalog.url))

        for package in packages:
            yield package

    def save_package(self, package):
        source_url = '%s#%s' % (self.catalog.url, package['identifier'])

        dataset = self.find_or_initialize(Dataset, country_code=self.catalog.country_code, name=package['identifier'])
        dataset.json = package
        dataset.custom_properties = [key for key, value in package.items() if value and key not in socrata_dataset_properties]
        dataset.source_url = source_url
        for dataset_property, column_name in dataset_properties.items():
            if package.get(dataset_property) is not None:
                setattr(dataset, column_name, package[dataset_property])

        dataset.save()

        for resource in package.get('distribution', []):
            distribution = self.find_or_initialize(Distribution, dataset=dataset, _id='%s#%s' % (package['identifier'], resource['format']))
            distribution.json = resource
            distribution.custom_properties = [key for key, value in resource.items() if value and key not in socrata_distribution_properties]
            distribution.country_code = dataset.country_code
            for distribution_property in socrata_distribution_properties:
                if resource.get(distribution_property) is not None:
                    setattr(distribution, distribution_property, resource[distribution_property])

            distribution.save()


socrata_dataset_properties = frozenset([
    'accessLevel',
    'contactPoint',
    'description',
    'distribution',
    'identifier',
    'keyword',
    'landingPage',
    'license',
    'mbox',
    'modified',
    'publisher',
    'theme',
    'title',
])
socrata_distribution_properties = frozenset([
    'accessURL',
    'format',
])

dataset_properties = {
    'accessLevel': 'accessLevel',
    'contactPoint': 'contactPoint',
    'description': 'description',
    'identifier': 'identifier',
    'keyword': 'keyword',
    'landingPage': 'landingPage',
    'license': 'license_id',
    'mbox': 'maintainer_email',
    'modified': 'modified',
    'publisher': 'publisher',
    'theme': 'theme',
    'title': 'title',
}
