import json
import re
from ast import literal_eval

import ckanapi
import requests
from django.db.utils import DataError

from .base import Scraper
from inventory.models import Dataset, Distribution

python_value_re = re.compile(r"\A\[u'")
gb_open_license_re = re.compile(r'open government licen[sc]e', re.IGNORECASE)


class CKANScraper(Scraper):
    def get_packages(self):
        # Create a CKAN client.
        # @note NL does not respond to GET requests.
        client = ckanapi.RemoteCKAN(self.url, get_only=self.country_code != 'nl')

        # Get all the packages.
        # @note 300,000 is the most datasets in any catalog.
        try:
            package_search = client.action.package_search(rows=300000)
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %sapi/3/action/package_search' % self.url)
            return

        packages_retrieved = len(package_search['results'])
        packages_count = package_search['count']

        # Confirm that the total number of packages is correct.
        # @note AR over-reports the "count" in package_search.
        if packages_retrieved != packages_count:
            try:
                package_list = client.action.package_list()
            except requests.packages.urllib3.exceptions.ProtocolError:
                self.error('ProtocolError %sapi/3/action/package_list' % self.url)
                return

            # package_list lists only the names of all packages.
            # @note US redirects package_list to to package_search.
            if isinstance(package_list, dict):  # package_search
                packages_count = package_list['count']
            else:
                packages_count = len(package_list)

        # Report the total number of packages.
        self.info('%d packages %s' % (packages_count, self.url))

        for package in package_search['results']:
            yield package

        # If we have to paginate.
        if packages_retrieved != packages_count:
            start = packages_retrieved  # zero-indexed
            while package_search['results']:
                print('.', end='', flush=True)

                try:
                    package_search = client.action.package_search(rows=packages_retrieved, start=start)
                except ckanapi.errors.CKANAPIError:
                    self.error('CKANAPIError %sapi/3/action/package_search?rows=%d&start=%d' % (self.url, packages_retrieved, start))
                except requests.packages.urllib3.exceptions.ProtocolError:
                    self.error('ProtocolError %sapi/3/action/package_search?rows=%d&start=%d' % (self.url, packages_retrieved, start))

                start += len(package_search['results'])

                for package in package_search['results']:
                    yield package

    def save_package(self, package):
        # GB lists packages for which no data is published.
        if self.country_code == 'gb' and package.get('unpublished') == 'true':
            return

        source_url = '%sapi/3/action/package_show?id=%s' % (self.url, package['name'])

        extras = {}

        # Try to make values uniform for use below.
        for extra in package.get('extras', []):
            value = extra['value']

            if isinstance(value, str):
                if python_value_re.match(value):
                    try:
                        value = literal_eval(value)
                    except ValueError as e:
                        log.warning('%s %s %s' % (e, value, source_url))
                elif value.startswith('['):
                    try:
                        value = json.loads(value)
                    except ValueError as e:
                        log.warning('%s %s %s' % (e, value, source_url))
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            if not isinstance(value, str):  # Value must be hashable for next() call below.
                value = json.dumps(value)

            if extra['key'] in extras and extra['value'] != extras[extra['key']]:
                log.warning('multiple %s %s' % (extra['key'], source_url))
            elif value:  # no clobber
                extras[extra['key']] = value

        # GB lists packages that it recognizes are not open data.
        # @see https://github.com/datagovuk/ckanext-dgu/blob/8b48fc88c9be8f3b5e3738ea96c9baab1a7deef0/ckanext/dgu/search_indexing.py#L71
        if self.country_code == 'gb' and not (
            package.get('license_id') == 'uk-ogl' or
            bool(gb_open_license_re.search(extras.get('licence', ''))) or
            bool(gb_open_license_re.search(extras.get('licence_url_title', '')))
        ):
            return

        dataset = self.find_or_initialize(Dataset, country_code=self.country_code, name=package['name'])
        dataset.json = package
        dataset.custom_properties = list(package.keys() - ckan_dataset_properties)
        dataset.source_url = source_url
        dataset.extras_keys = list(set(extras.keys()))

        for dataset_property, column_name in dataset_properties.items():
            if package.get(dataset_property):
                setattr(dataset, column_name, package[dataset_property])
        for license_property in license_properties:
            if package.get(license_property):
                setattr(dataset, license_property, package[license_property])

        # Determine the license_id.
        license_id = package.get('license_id')
        if not license_id:
            # License URLs have been found in "licence_url", "licence_url_title" and "access_constraints".
            match = next((value for value in extras.values() if value in licence_url_to_license_id), None)
            if match:
                license_id = licence_url_to_license_id[match]
            elif self.country_code == 'gb' and extras.get('licence') == 'Open Government Licence':
                license_id = 'uk-ogl'
            elif package.get('license_title') or package.get('license_url'):
                log.warning('license_title or license_url but no license_id %s' % source_url)

        if license_id:
            dataset.license_id = license_id

        # Set the license_url and license_title from extras if not yet set. The
        # license_url and license_title should agree with the extra licence_url
        # and licence_url_title.
        if extras.get('licence_url'):
            if package.get('license_url'):
                if extras.get('licence_url') != package.get('license_url') and not (
                    # @note AU's "licence_url" uses a different URL for "cc-by".
                    self.country_code == 'au' and
                    extras.get('licence_url') == 'http://www.opendefinition.org/licenses/cc-by' and
                    package.get('license_url') == 'http://creativecommons.org/licenses/by/3.0/au/'
                ):
                    log.warning('extras.licence_url expected %s got %s' % (package.get('license_url'), extras.get('licence_url')))
            elif license_id:  # only runs if license_url not previously set
                dataset.license_url = extras.get('licence_url')
            else:
                log.warning('extras.licence_url but no license_id %s' % source_url)
        if extras.get('licence_url_title'):
            if package.get('license_title'):
                if extras.get('licence_url_title') != package.get('license_title'):
                    log.warning('extras.licence_url_title expected %s got %s' % (package.get('license_title'), extras.get('licence_url_title')))
            elif license_id:  # only runs if license_title not previously set
                dataset.license_title = extras.get('licence_url_title')
            else:
                log.warning('extras.licence_url_title but no license_id %s' % source_url)

        try:
            dataset.save()

            for resource in package['resources']:
                distribution = self.find_or_initialize(Distribution, dataset=dataset, _id=resource['id'])
                distribution.json = resource
                distribution.custom_properties = list(resource.keys() - ckan_distribution_properties)

                for distribution_property, column_name in distribution_properties.items():
                    if resource.get(distribution_property):
                        setattr(distribution, column_name, resource[distribution_property])

                distribution.save()

        except DataError as e:
            try:
                if len(distribution.url) > 600:
                    log.error('distribution.url is %d' % len(distribution.url))
            except NameError:
                if len(dataset.source_url) > 200:
                    log.error('dataset.source_url is %d' % len(dataset.source_url))
                if len(dataset.url) > 500:
                    log.error('dataset.url is %d' % len(dataset.url))
                if len(dataset.license_url) > 200:
                    log.error('dataset.license_url is %d' % len(dataset.license_url))
                if len(dataset.maintainer_email) > 254:
                    log.error('dataset.maintainer_email is %d' % len(dataset.maintainer_email))
                if len(dataset.author_email) > 254:
                    log.error('dataset.author_email is %d' % len(dataset.author_email))
        except KeyError as e:
            log.error('%s missing key %s' % (source_url, e))


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
    'id',
    'created',
    'description',
    'format',
    'mimetype',
    'last_modified',
    'name',
    'size',
    'url',

    # Not modeled
    'cache_last_updated',
    'cache_url',
    'hash',
    'mimetype_inner',
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
    'tags': 'keyword',
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
    'mimetype': 'mediaType',
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
    'http://inspire.halton.gov.uk/eul':
        'Halton Licence (Inaccessible)',

    'http://www.barrowbc.gov.uk/giscopyright':
        'Barrow Borough Council Licence (Inaccessible)',

    'http://broads-authority.gov.uk/copyright.html':
        'Terms of Use for Broads Authority Information and Data',

    'http://eidchub.ceh.ac.uk/administration-folder/tools/ceh-standard-licence-texts/grant-of-licence-for-web-mapping-services/plain':
        'Centre for Ecology & Hydrology Natural Environment Research Council Licence',

    'http://www.metoffice.gov.uk/about-us/legal/fair-usage':
        'met-office-cp',

    'http://www.nationalarchives.gov.uk/doc/open-government-licence/':
        'uk-ogl',
    'http://ACwww.nationalarchives.gov.uk/doc/open-government-licence/':
        'uk-ogl',
    'http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/':
        'uk-ogl',
    'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/':
        'uk-ogl',

    'http://www.naturalengland.org.uk/copyright':
        'Publicly accessible Natural England - OS OGL',
    'http://www.naturalengland.org.uk/copyright/default.aspx':
        'Publicly accessible Natural England - OS OGL',

    'http://www.ordnancesurvey.co.uk/oswebsite/licensing/index.html':
        'Unspecified Ordnance Survey License',
    'http://www.ordnancesurvey.co.uk/business-and-government/licensing/index.html':
        'Unspecified Ordnance Survey License',

    'http://www.ordnancesurvey.co.uk/docs/licences/os-opendata-licence.pdf':
        'OS Open Data Licence',
    'http://www.ordnancesurvey.co.uk/oswebsite/docs/licences/os-opendata-licence.pdf':
        'OS Open Data Licence',

    'http://www.ordnancesurvey.co.uk/business-and-government/public-sector/mapping-agreements/psma-licensing.html':
        'PSMA',

    'http://www.ordnancesurvey.co.uk/business-and-government/public-sector/mapping-agreements/end-user-licence.html':
        'Public Sector End User Licence',

    'http://www.ordnancesurvey.co.uk/docs/licences/public-sector-end-user-licence-inspire.htm':
        'Public Sector End User Licence - INSPIRE',
    'http://www.ordnancesurvey.co.uk/business-and-government/public-sector/mapping-agreements/inspire-licence.h':
        'Public Sector End User Licence - INSPIRE',
    'http://www.ordnancesurvey.co.uk/business-and-government/public-sector/mapping-agreements/inspire-licence.htm':
        'Public Sector End User Licence - INSPIRE',
    'http://www.ordnancesurvey.co.uk/business-and-government/public-sector/mapping-agreements/inspire-licence.html':
        'Public Sector End User Licence - INSPIRE',
    'http://www.ordnancesurvey.co.uk/business-and-government /public-sector/mapping-agreements/inspire-licence.html':
        'Public Sector End User Licence - INSPIRE',
    'http://www.ordanancesurvey.co.uk/business-and-government/public-sector/mapping-agreements/inspire-license.html':
        'Public Sector End User Licence - INSPIRE',

    'http://www.ordnancesurvey.co.uk/business-and-government/licensing/licences/web-mapping-service-end-user-licence.html':
        'Public Sector INSPIRE WMS End User Licence',
    'http://www.ordnancesurvey.co.uk/business-and-government/licensing/licences/web-mapping-service-end-user-licence.html?utm_source=Web%2Bmapping%2Bservice%2Bviewer&utm_medium=Redirect&utm_term=wmseul&utm_campaign=INSPIRE':
        'Public Sector INSPIRE WMS End User Licence',
    'http://tinyurl.com/OS-INSPIRE-End-User-Licence':
        'Public Sector INSPIRE WMS End User Licence',

    'http://mapsonline.dundeecity.gov.uk/uat_dcc_gis_root/dcc_gis_config/app_config/INSPIRE/final-osma2-eul-inspire-wms-v1-0-readonly.pdf':
        'Public Sector INSPIRE WMS End User Licence (Scotland)',
}
