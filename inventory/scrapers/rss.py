import requests
from datetime import datetime
from lxml import etree

from .base import Scraper
from ..models import Dataset


class RSS(Scraper):
    def get_packages(self):
        try:
            response = requests.get(self.catalog.url)
            packages = etree.fromstring(response.content).xpath('//item')
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %s' % self.catalog.url)
            return

        self.info('%d packages %s' % (len(packages), self.catalog.url))

        for package in packages:
            yield package

    def save_package(self, package):
        identifier = package.xpath('./guid')[0].text

        source_url = '%s#%s' % (self.catalog.url, identifier)

        dataset = self.find_or_initialize(Dataset, division_id=self.catalog.division_id, name=identifier)
        dataset.custom_properties = [tag for tag in map(lambda node: node.tag, package.xpath('./*')) if tag not in rss_dataset_properties]
        dataset.source_url = source_url
        for dataset_property, column_name in dataset_properties.items():
            value = self.get_value(package, dataset_property)
            if value is not None:
                setattr(dataset, column_name, value)
        dataset.issued = datetime.strptime(package.xpath('./pubDate')[0].text, '%a, %d %b %Y %H:%M:%S +0000')
        dataset.keyword = [category.attrib['domain'] for category in package.xpath('./category')]

        dataset.save()

    def get_values(self, node, path):
        values = []
        for child in node.xpath(path, namespaces={'dc': 'http://purl.org/dc/elements/1.1/'}):
            value = child.text
            if value:
                values.append(value)
        return values

    def get_value(self, node, path):
        values = self.get_values(node, path)
        if len(values) == 1:
            return values[0]
        elif len(values) > 1:
            raise Exception('expected zero or one %s' % (path))

rss_dataset_properties = frozenset([
    'title',
    'description',
    'pubDate',
    '{http://purl.org/dc/elements/1.1/}creator',
    'guid',
    'category',
    'link',
    'comments',
])

dataset_properties = {
    './title': 'title',
    './description': 'description',
    './dc:creator': 'publisher',
    './guid': 'identifier',
    './link': 'landingPage',
}
