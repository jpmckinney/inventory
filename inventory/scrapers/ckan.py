import json
import re
from ast import literal_eval

import ckanapi
import requests
from django.db.utils import DataError

from .base import Scraper
from ..models import Dataset, Distribution

citation_re = re.compile(r'\b(?:citation|mu[cs]t (?:acknowledge|cite|be attributed))\b')
python_value_re = re.compile(r"\A\[u'")
gb_open_license_re = re.compile(r'open government licen[sc]e', re.IGNORECASE)


class CKAN(Scraper):
    def get_packages(self):
        url = self.catalog.url

        # Create a CKAN client.
        # @note NL does not respond to GET requests.
        client = ckanapi.RemoteCKAN(url, get_only=self.catalog.get_only)

        # Get all the packages.
        # @note 300,000 is the most datasets in any catalog.
        try:
            package_search = client.action.package_search(rows=300000, **self.catalog.parameters)
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %sapi/3/action/package_search' % url)
            return

        packages_retrieved = len(package_search['results'])
        packages_count = package_search['count']

        # Confirm that the total number of packages is correct.
        # @note AR over-reports the "count" in package_search.
        if packages_retrieved != packages_count and not self.catalog.parameters:
            try:
                package_list = client.action.package_list()
            except requests.packages.urllib3.exceptions.ProtocolError:
                self.error('ProtocolError %sapi/3/action/package_list' % url)
                return

            # package_list lists only the names of all packages.
            # @note US redirects package_list to to package_search.
            if isinstance(package_list, dict):  # package_search
                packages_count = package_list['count']
            else:
                packages_count = len(package_list)

        # Report the total number of packages.
        self.info('%d packages %s' % (packages_count, url))

        for package in package_search['results']:
            yield package

        # If we have to paginate.
        if packages_retrieved != packages_count:
            start = packages_retrieved  # zero-indexed
            while package_search['results']:
                print('.', end='', flush=True)

                try:
                    package_search = client.action.package_search(rows=packages_retrieved, start=start, **self.catalog.parameters)
                except ckanapi.errors.CKANAPIError:
                    self.error('CKANAPIError %sapi/3/action/package_search?rows=%d&start=%d' % (url, packages_retrieved, start))
                except requests.packages.urllib3.exceptions.ProtocolError:
                    self.error('ProtocolError %sapi/3/action/package_search?rows=%d&start=%d' % (url, packages_retrieved, start))

                start += len(package_search['results'])

                for package in package_search['results']:
                    yield package

    def save_package(self, package):
        source_url = '%sapi/3/action/package_show?id=%s' % (self.catalog.url, package['name'])

        extras = {}

        # Change extras from a list to a dictionary and make values uniform.
        for extra in package.get('extras', []):
            value = extra['value']

            if isinstance(value, str):
                if python_value_re.search(value):
                    try:
                        value = literal_eval(value)
                    except ValueError as e:
                        self.warning('%s %s %s' % (e, value, source_url))
                elif value.startswith('['):
                    try:
                        value = json.loads(value)
                    except ValueError as e:
                        self.warning('%s %s %s' % (e, value, source_url))
            if isinstance(value, list):
                try:
                    value = list(set(value))
                except TypeError:  # a list of dict is unhashable
                    pass
                if len(value) == 1:
                    value = value[0]
            if not isinstance(value, str):  # Value must be hashable for next() call below.
                value = json.dumps(value)

            if value:
                if extra['key'] in extras:  # no clobber
                    if value != extras[extra['key']]:
                        self.warning('multiple %s %s' % (extra['key'], source_url))
                else:
                    extras[extra['key']] = value

        dataset = self.find_or_initialize(Dataset, country_code=self.catalog.country_code, name=package['name'])
        dataset.json = package
        dataset.custom_properties = [key for key, value in package.items() if value and key not in ckan_dataset_properties]
        dataset.source_url = source_url
        dataset.extras = extras
        dataset.extras_keys = list(set(extras.keys()))
        for dataset_property, column_name in dataset_properties.items():
            if package.get(dataset_property) is not None:
                setattr(dataset, column_name, package[dataset_property])
        for license_property in license_properties:
            if package.get(license_property) is not None:
                setattr(dataset, license_property, package[license_property])

        # "name" is always equal to "display_name", "vocabulary_id" is
        # either null or opaque, and "state" is always "active".
        # SELECT DISTINCT t FROM (SELECT json_array_elements(keyword)->>'vocabulary_id' t FROM inventory_dataset WHERE keyword::text <> '{}'::text) v WHERE t IS NOT NULL;
        # SELECT t FROM (SELECT json_array_elements(keyword)->>'state' t FROM inventory_dataset WHERE keyword::text <> '{}'::text) v WHERE t != 'active';
        # SELECT a, b FROM (SELECT json_array_elements(keyword)->>'name' a, json_array_elements(keyword)->>'display_name' b FROM inventory_dataset WHERE keyword::text <> '{}'::text) v WHERE a != b;
        dataset.keyword = [tag['name'] for tag in package.get('tags', [])]

        # Determine the license_id.
        license_id = package.get('license_id')
        if not license_id:
            # License URLs have been found in "licence_url", "licence_url_title" and "access_constraints".
            match = next((value for value in extras.values() if value in licence_url_to_license_id), None)
            if match:
                license_id = licence_url_to_license_id[match]
            # @note GB ought to clean up its licensing.
            elif self.catalog.country_code == 'gb':
                licence = extras.get('licence')
                if licence in (
                    'Contains public sector information licensed under the Open Government Licence v2.0',
                    'Licence terms and conditions apply (Open Government Licence)',
                    'Open Data available for use under the Open Government Licence',
                    'Open Government Licence',
                    'Open Government Licence - http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/',
                    'Open Government Licence, http://www.nationalarchives.gov.uk/doc/open-government-licence',
                    'Open Government Licence, http://www.nationalarchives.gov.uk/doc/open-government-licence/',
                    'Open Government License',
                    'Open Government License (http://www.nationalarchives.gov.uk/doc/open-government-licence/)',
                    'Open Government License.',
                    'Use of this data is subject to acceptance of the Open Government Licence',
                    '["No conditions apply", "None", "Open Government License (OGL)"]',
                    '["None", "Open Government License (OGL)"]',
                ):
                    license_id = 'uk-ogl'
                elif 'www.naturalengland.org.uk/copyright/default.aspx' in licence:
                    license_id = 'Natural England-OS Open Government Licence'
                elif 'https://www.ordnancesurvey.co.uk/opendatadownload/products.html' in licence:
                    license_id = 'OS OpenData Licence'
                elif citation_re.search(licence):
                    license_id = 'uk-citation-required'
            elif package.get('license_title') or package.get('license_url'):
                self.warning('license_title or license_url but no license_id %s' % source_url)

        if license_id:
            dataset.license_id = license_id

        # Set the license_url and license_title from extras if not yet set. The
        # license_url and license_title should agree with the extra licence_url
        # and licence_url_title.
        if extras.get('licence_url'):
            if package.get('license_url'):
                if extras.get('licence_url') != package.get('license_url') and not (
                    # @note AU's "licence_url" uses a different, valid URL for "cc-by".
                    self.catalog.country_code == 'au' and
                    extras.get('licence_url') == 'http://www.opendefinition.org/licenses/cc-by' and
                    package.get('license_url') == 'http://creativecommons.org/licenses/by/3.0/au/'
                ):
                    self.warning('extras.licence_url expected %s got %s' % (package.get('license_url'), extras.get('licence_url')))
            elif license_id:  # only runs if license_url not previously set
                dataset.license_url = extras.get('licence_url')
            else:
                self.warning('extras.licence_url but no license_id %s' % source_url)
        if extras.get('licence_url_title'):
            if package.get('license_title'):
                if extras.get('licence_url_title') != package.get('license_title'):
                    self.warning('extras.licence_url_title expected %s got %s' % (package.get('license_title'), extras.get('licence_url_title')))
            elif license_id:  # only runs if license_title not previously set
                dataset.license_title = extras.get('licence_url_title')
            else:
                self.warning('extras.licence_url_title but no license_id %s' % source_url)

        try:
            dataset.save()

            for resource in package['resources']:
                distribution = self.find_or_initialize(Distribution, dataset=dataset, _id=resource['id'])
                distribution.json = resource
                distribution.custom_properties = [key for key, value in resource.items() if value and key not in ckan_distribution_properties]
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
ckan_dataset_properties = frozenset([
    # package_search retrieves the id and data_dict fields from Solr. The
    # data_dict field is populated with the output of package_show, which
    # respects default_show_package_schema and passes the package through
    # package_dictize... It's easier to just look at the CKAN API output.

    # Modeled
    'author',
    'author_email',
    'id',
    'isopen',
    'license_id',
    'license_title',
    'license_url',
    'maintainer',
    'maintainer_email',
    'metadata_created',
    'metadata_modified',
    'name',
    'notes',
    'owner_org',
    'tags',
    'title',
    'url',

    # Not modeled
    'creator_user_id',
    'extras',
    'groups',
    'num_resources',
    'num_tags',
    'organization',
    'private',
    'relationships_as_object',
    'relationships_as_subject',
    'resources',
    'revision_id',
    'revision_timestamp',
    'state',
    'tracking_summary',
    'type',
    'version',
])
ckan_distribution_properties = frozenset([
    # Modeled
    'created',
    'description',
    'format',
    'id',
    'last_modified',
    'mimetype',
    'mimetype_inner',
    'name',
    'size',
    'url',

    # Not modeled
    'cache_last_updated',
    'cache_url',
    'hash',
    'position',
    'resource_group_id',
    'resource_type',
    'revision_id',
    'revision_timestamp',
    'state',
    'tracking_summary',
    'url_type',
    'webstore_last_updated',
    'webstore_url',
])

# Map CKAN properties to model properties.
dataset_properties = {
    'title': 'title',
    'notes': 'description',
    'metadata_created': 'issued',
    'metadata_modified': 'modified',
    'owner_org': 'publisher',
    'id': 'identifier',
    'maintainer': 'maintainer',  # dcat:contactPoint vcard:fn
    'maintainer_email': 'maintainer_email',  # dcat:contactPoint vcard:hasEmail
    'author': 'author',  # dcat:contactPoint vcard:fn
    'author_email': 'author_email',  # dcat:contactPoint vcard:hasEmail
    'url': 'landingPage',

    # CKAN doesn't have:
    # * dct:language
    # * dct:accrualPeriodicity
    # * dct:spatial
    # * dct:temporal
    # * dcat:theme
}
distribution_properties = {
    'name': 'title',
    'description': 'description',
    'created': 'issued',
    'last_modified': 'modified',
    'url': 'accessURL',
    'size': 'byteSize',
    'mimetype': 'mimetype',
    'mimetype_inner': 'mimetype_inner',
    'format': 'format',

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
