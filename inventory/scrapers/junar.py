from datetime import datetime

import requests

from .base import Scraper
from ..models import Dataset, Distribution

class Junar(Scraper):
    # The Junar API has no endpoint for listing all datasets. Junar has
    # dashboards, datastreams, dataviews and visualizations.
    #
    # Sending an invalid search query exposes the Solr query:
    # http://paloalto.cloudapi.junar.com/datastreams/search?query=*&auth_key=ba2193005ea48700020ac26185687a5f821e5e95
    # We can thus craft a search query to match all documents:
    # http://paloalto.cloudapi.junar.com/datastreams/search?query=type:ds&auth_key=ba2193005ea48700020ac26185687a5f821e5e95
    # However, only a maximum of 100 are returned.
    #
    # The datastreams/top endpoint seems to limit max_results to 85:
    # http://api.recursos.datos.gob.cl/datastreams/top?auth_key=6ae305b9ad9923f768879e851addf143c3461182&max_results=85
    #
    # The Junar API client doesn't implement search.
    # @see https://github.com/Junar/junar-api-python-client
    def get_packages(self):
        # This query matches all documents, to a maximum of 100.
        params = {'query': 'type:ds'}
        params.update(self.catalog.parameters)

        try:
            packages = requests.get(self.catalog.url + 'datastreams/search', params=params).json()
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %s' % self.catalog.url)
            return

        self.info('%d packages %s' % (len(packages), self.catalog.url))

        for package in packages:
            yield package

    def save_package(self, package):
        source_url = package['link']

        dataset = self.find_or_initialize(Dataset, country_code=self.catalog.country_code, name=package['id'])
        dataset.json = package
        dataset.custom_properties = [key for key, value in package.items() if value and key not in junar_dataset_properties]
        dataset.source_url = source_url
        for dataset_property, column_name in dataset_properties.items():
            if package.get(dataset_property) is not None:
                setattr(dataset, column_name, package[dataset_property])
        if package.get('created_at') is not None:
            dataset.issued = datetime.utcfromtimestamp(int(package['created_at']))

        dataset.save()

junar_dataset_properties = frozenset([
    'description',
    'tags',
    'created_at',
    'title',
    'link',
    'id',
])

dataset_properties = {
    'title': 'title',
    'description': 'description',
    'tags': 'keyword',
    'created_at': 'issued',
    'id': 'identifier',
    'link': 'landingPage',
}
