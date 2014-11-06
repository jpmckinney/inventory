import json
import re
from ast import literal_eval

import requests
from django.db.utils import DataError

from .base import Scraper
from ..models import Dataset, Distribution

citation_re = re.compile(r'\b(?:citation|mu[cs]t (?:acknowledge|cite|be attributed))\b')
python_value_re = re.compile(r"\A\[u'")
gb_open_license_re = re.compile(r'open government licen[sc]e', re.IGNORECASE)


class Socrata(Scraper):
    def get_packages(self):
        url = self.catalog.url + 'data.json'

        # Get all the packages.
        try:
            package_raw = requests.get(url).json()
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %s' % url)
            return

        packages_count = len(package_raw)


        # Report the total number of packages.
        self.info('%d packages %s' % (packages_count, url))

        for package in package_raw:

            yield package



    def save_package(self, package):
        source_url = '%s - %s' % (self.catalog.url, package['identifier'])

        extras = {}


        dataset = self.find_or_initialize(Dataset, country_code=self.catalog.country_code, name=package['identifier'])
        dataset.json = package
        dataset.custom_properties = [key for key, value in package.items() if value and key not in socrata_dataset_properties]
        dataset.source_url = source_url

        for dataset_property, column_name in dataset_properties.items():
            if package.get(dataset_property) is not None:
                setattr(dataset, column_name, package[dataset_property])
        for license_property in license_properties:
            if package.get(license_property) is not None:
                setattr(dataset, license_property, package[license_property])

        # Determine the license_id.
        license_id = package.get('license')

        #TODO - We might need some processing to get the licence ID.

        if license_id:
            dataset.license_id = license_id


        try:
            dataset.save()

            if package['identifier'] != 'data.json':
                for resource in package['distribution']:
                    distribution = self.find_or_initialize(Distribution, dataset=dataset, _id=package['identifier']+resource['format'])
                    distribution.json = resource
                    distribution.custom_properties = [key for key, value in resource.items() if value and key not in socrata_distribution_properties]
                    distribution.country_code = dataset.country_code
                    for distribution_property, column_name in distribution_properties.items():
                        if resource.get(distribution_property) is not None:
                            setattr(distribution, column_name, resource[distribution_property])

                    distribution.save()

        except DataError as e:
            try:
                if len(distribution.accessURL) > 2000:
                    self.error('distribution.accessURL is %d' % len(distribution.accessURL))
            except NameError:
                if len(dataset.name) > 100:
                    self.error('dataset.name is %d' % len(dataset.name))
                if len(dataset.source_url) > 200:
                    self.error('dataset.source_url is %d' % len(dataset.source_url))
                if len(dataset.landingPage) > 500:
                    self.error('dataset.landingPage is %d' % len(dataset.landingPage))
                if len(dataset.license_url) > 200:
                    self.error('dataset.license_url is %d' % len(dataset.license_url))
                if len(dataset.maintainer_email) > 254:
                    self.error('dataset.maintainer_email is %d' % len(dataset.maintainer_email))
                if len(dataset.author_email) > 254:
                    self.error('dataset.author_email is %d' % len(dataset.author_email))
        except KeyError as e:
            self.error('%s missing key %s' % (source_url, e))


# Core CKAN fields.
socrata_dataset_properties = frozenset([
    # package_search retrieves the id and data_dict fields from Solr. The
    # data_dict field is populated with the output of package_show, which
    # respects default_show_package_schema and passes the package through
    # package_dictize... It's easier to just look at the CKAN API output.

    # Modeled
    'contactPoint',
    'mbox',
    'identifier',
    'license',
    'issued',
    'modified',
    'description',
    'publisher',
    'keyword',
    'title',
    'landingPage',

    # Not modeled
    'spatial',
    'temporal',
    'accrualPeriodicity', 
    'language',
    'dataQuality',
    'theme',
    'references',

])
socrata_distribution_properties = frozenset([
    # Modeled
    'accessURL',
    'format'

])

# Map CKAN properties to model properties.
dataset_properties = {
    'contactPoint':'contactPoint',
    'mbox':'mbox',
    'identifier':'identifier',
    'license':'license',
    'issued':'issued',
    'modified':'modified',
    'description':'description',
    'publisher':'publisher',
    'keyword':'keyword',
    'title':'title',
    'landingPage':'landingPage',

    # CKAN doesn't have:
    # * dct:language
    # * dct:accrualPeriodicity
    # * dct:spatial
    # * dct:temporal
    # * dcat:theme
}
distribution_properties = {
    'accessURL':'accessURL',
    'format':'format'

    # CKAN doesn't have:
    # * dcat:downloadURL
    # * dct:license
    # * dct:rights
}

license_properties = frozenset([
    'isopen',
    'license_title',
    'license_url',
])

# GB often uses "extras" for licensing, but has no "licence_id" under "extras".
licence_url_to_license_id = {
    'http://ACwww.nationalarchives.gov.uk/doc/open-government-licence/':
        'uk-ogl',
    'http://www.nationalarchives.gov.uk/doc/open-government-licence/':
        'uk-ogl',
    'http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/':
        'uk-ogl',
    'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/':
        'uk-ogl',
    'http://www.naturalengland.org.uk/copyright/default.aspx':
        'Natural England-OS Open Government Licence',
    'http://www.ordnancesurvey.co.uk/docs/licences/os-opendata-licence.pdf':
        'OS OpenData Licence',
    'http://www.ordnancesurvey.co.uk/oswebsite/docs/licences/os-opendata-licence.pdf':
        'OS OpenData Licence',
}
