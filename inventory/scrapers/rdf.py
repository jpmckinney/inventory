import requests
from lxml import etree

from .base import Scraper
from ..models import Dataset, Distribution

class RDF(Scraper):
    def get_packages(self):
        # Transforming a graph of triples with rdflib into Django objects is
        # complicated. We can use rdflib to find all the predicates, and then
        # parse the XML with that knowledge:
        #
        # import rdflib
        # graph = rdflib.Graph()
        # graph.load(self.catalog.url)
        # set([predicate for _, predicate, _ in graph])

        try:
            response = requests.get(self.catalog.url)
            packages = self.xpath(etree.fromstring(response.content), '//dcat:Dataset')
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %s' % self.catalog.url)
            return

        self.info('%d packages %s' % (len(packages), self.catalog.url))

        for package in packages:
            yield package

    def save_package(self, package):
        identifier = package.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', self.xpath(package, './/dcat:Distribution/@rdf:about')[0])

        source_url = '%s#%s' % (self.catalog.url, identifier)

        dataset = self.find_or_initialize(Dataset, country_code=self.catalog.country_code, name=identifier)
        dataset.custom_properties = [tag for tag in map(lambda node: node.tag, package.xpath('./*')) if tag not in rdf_dataset_properties]
        dataset.source_url = source_url
        for dataset_property, column_name in dataset_properties.items():
            if column_name in ('keyword', 'theme'):
                values = self.get_values(package, dataset_property)
                if values:
                    setattr(dataset, column_name, values)
            elif column_name in ('description', 'language', 'spatial', 'title'):
                values = self.get_values(package, dataset_property)
                if values:
                    setattr(dataset, column_name, values[0])
            elif column_name in ('issued', 'modified'):
                value = self.get_value(package, dataset_property)
                if value is not None and value not in ('T00:00:00Z', 'Z'):
                    setattr(dataset, column_name, value.replace('ZZ', 'Z'))  # e.g. "2010-11-17T00:00:00ZZ"
            else:
                value = self.get_value(package, dataset_property)
                if value is not None:
                    setattr(dataset, column_name, value)

        dataset.save()

        for resource in self.xpath(package, './/dcat:Distribution'):
            distribution = self.find_or_initialize(Distribution, dataset=dataset, _id=resource.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'])
            distribution.custom_properties = [tag for tag in map(lambda node: node.tag, resource.xpath('./*')) if tag not in rdf_distribution_properties]
            distribution.country_code = dataset.country_code
            for distribution_property, column_name in distribution_properties.items():
                if column_name in ('description', 'title'):
                    values = self.get_values(resource, distribution_property)
                    if values:
                        setattr(distribution, column_name, values[0])
                else:
                    value = self.get_value(resource, distribution_property)
                    if value is not None:
                        setattr(distribution, column_name, value)

            distribution.save()

    def xpath(self, node, path):
        return node.xpath(path, namespaces={
            'dc': 'http://purl.org/dc/elements/1.1/',
            'dcat': 'http://www.w3.org/ns/dcat#',
            'dct': 'http://purl.org/dc/terms/',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        })

    def get_values(self, node, path):
        values = []
        for child in self.xpath(node, path):
            value = child.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', child.text)
            if value:
                values.append(value)
        return values

    def get_value(self, node, path):
        values = self.get_values(node, path)
        if len(values) == 1:
            return values[0]
        elif len(values) > 1:
            raise Exception('expected zero or one %s' % (path))


rdf_dataset_properties = frozenset([
    '{http://purl.org/dc/terms/}title',
    '{http://purl.org/dc/terms/}description',
    '{http://purl.org/dc/terms/}issued',
    '{http://purl.org/dc/terms/}modified',
    '{http://purl.org/dc/elements/1.1/}language',
    '{http://purl.org/dc/terms/}publisher',
    '{http://purl.org/dc/terms/}identifier',
    '{http://purl.org/dc/terms/}spatial',
    '{http://www.w3.org/ns/dcat#}theme',
    '{http://www.w3.org/ns/dcat#}keyword',
    '{http://purl.org/dc/terms/}license',
    '{http://www.w3.org/ns/dcat#}distribution',
    '{http://purl.org/dc/terms/}accrualPeriodicity',
    '{http://purl.org/dc/terms/}temporal',
    '{http://purl.org/dc/terms/}conformsTo',
    '{http://purl.org/dc/terms/}references',
    '{http://purl.org/dc/terms/}valid',
])

rdf_distribution_properties = frozenset([
    '{http://purl.org/dc/terms/}title',
    '{http://purl.org/dc/terms/}description',
    '{http://purl.org/dc/terms/}issued',
    '{http://purl.org/dc/terms/}modified',
    '{http://purl.org/dc/terms/}license',
    '{http://www.w3.org/ns/dcat#}accessURL',
    '{http://www.w3.org/ns/dcat#}byteSize',
    '{http://purl.org/dc/terms/}format',
    '{http://purl.org/dc/terms/}relation',
])

dataset_properties = {
    './dct:title': 'title',
    './dct:description': 'description',
    './dct:issued': 'issued',
    './dct:modified': 'modified',
    './dc:language': 'language',
    './dct:publisher': 'publisher',
    './dct:identifier': 'identifier',
    './dct:spatial': 'spatial',
    './dcat:theme': 'theme',
    './dcat:keyword': 'keyword',
    './dct:license': 'license',
    # dcat:distribution
    # dct:accrualPeriodicity
    # dct:temporal
    # dct:conformsTo "Normativa" (url)
    # dct:references "Otros recursos" (url)
    # dct:valid "Vigencia del recurso" (date-time)
}
distribution_properties = {
    './dct:title': 'title',
    './dct:description': 'description',
    './dct:issued': 'issued',
    './dct:modified': 'modified',
    './dct:license': 'license',
    './dcat:accessURL': 'accessURL',
    './dcat:byteSize': 'byteSize',
    './dct:format': 'format',
    # dct:relation "+info" (text, url)
}

# Catalog properties
# * dct:extent
# * dct:language
# * dcat:dataset
# * dcat:themeTaxonomy
# * http://xmlns.com/foaf/0.1/homepage

# Generic RDF properties
# * http://www.w3.org/1999/02/22-rdf-syntax-ns#type
# * http://www.w3.org/1999/02/22-rdf-syntax-ns#value
# * http://www.w3.org/2000/01/rdf-schema#label
# * http://www.w3.org/2006/time#days
# * http://www.w3.org/2006/time#hasBeginning
# * http://www.w3.org/2006/time#hasEnd
# * http://www.w3.org/2006/time#inXSDDateTime
# * http://www.w3.org/2006/time#months
# * http://www.w3.org/2006/time#years

# The predicate is either time:days, time:months or time:years.
#
# <dct:accrualPeriodicity>
#     <dct:Frequency>
#         <rdf:value>
#             <time:DurationDescription>
#                 <time:days rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</time:days>
#             </time:DurationDescription>
#         </rdf:value>
#     </dct:Frequency>
# </dct:accrualPeriodicity>

# <dct:temporal>
#     <time:Interval>
#         <rdf:type rdf:resource="http://purl.org/dc/terms/PeriodOfTime" />
#     </time:Interval>
# </dct:temporal>
#
# <dct:temporal>
#     <time:Interval>
#         <rdf:type rdf:resource="http://purl.org/dc/terms/PeriodOfTime" />
#         <time:hasBeginning>
#             <time:Instant>
#                 <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2000-07-01T13:39:00Z</time:inXSDDateTime>
#             </time:Instant>
#         </time:hasBeginning>
#         <time:hasEnd>
#             <time:Instant>
#                 <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2000-07-01T13:39:00Z</time:inXSDDateTime>
#             </time:Instant>
#         </time:hasEnd>
#     </time:Interval>
# </dct:temporal>
