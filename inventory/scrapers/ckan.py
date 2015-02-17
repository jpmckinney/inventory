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
        client = ckanapi.RemoteCKAN(url, get_only=self.catalog.get_only)

        # Get all the packages.
        try:
            data_dict = self.catalog.parameters.copy()
            data_dict['rows'] = 300000  # the most datasets in any catalog
            package_search = client.call_action('package_search', data_dict=data_dict, verify=self.catalog.verify)
        except requests.packages.urllib3.exceptions.ProtocolError:
            self.error('ProtocolError %sapi/3/action/package_search' % url)
            return

        packages_retrieved = len(package_search['results'])
        packages_count = package_search['count']

        # Confirm that the total number of packages is correct.
        # @note AR over-reports the "count" in package_search.
        if packages_retrieved != packages_count and not self.catalog.parameters:
            try:
                package_list = client.call_action('package_list', verify=self.catalog.verify)
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
                    data_dict = self.catalog.parameters.copy()
                    data_dict['rows'] = packages_retrieved
                    data_dict['start'] = start
                    package_search = client.call_action('package_search', data_dict=data_dict, verify=self.catalog.verify)
                except ckanapi.errors.CKANAPIError:
                    self.error('CKANAPIError %sapi/3/action/package_search?rows=%d&start=%d' % (url, packages_retrieved, start))
                except requests.packages.urllib3.exceptions.ProtocolError:
                    self.error('ProtocolError %sapi/3/action/package_search?rows=%d&start=%d' % (url, packages_retrieved, start))

                start += len(package_search['results'])

                for package in package_search['results']:
                    yield package

    def save_package(self, package):
        if package['type'] == 'harvest':  # harvest packages contain packages, not resources
            return

        if self.catalog.division_id == 'ocd-division/country:it' and package['organization'] and package['organization']['name'] not in organization_names:
            return

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

        dataset = self.find_or_initialize(Dataset, division_id=self.catalog.division_id, name=package['name'])
        dataset.json = package
        dataset.custom_properties = [k for k, v in package.items() if v and k not in ckan_dataset_properties]
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
        #
        # SELECT DISTINCT t FROM (SELECT json_array_elements(keyword)->>'vocabulary_id' t FROM inventory_dataset WHERE keyword::text <> '{}'::text) v WHERE t IS NOT NULL;
        # SELECT t FROM (SELECT json_array_elements(keyword)->>'state' t FROM inventory_dataset WHERE keyword::text <> '{}'::text) v WHERE t != 'active';
        # SELECT a, b FROM (SELECT json_array_elements(keyword)->>'name' a, json_array_elements(keyword)->>'display_name' b FROM inventory_dataset WHERE keyword::text <> '{}'::text) v WHERE a != b;
        dataset.keyword = [tag['name'] for tag in package.get('tags', [])]

        dataset.language = oneof(package, 'language', 'original_language')
        dataset.accrualPeriodicity = oneof(package, 'frekuensi_penerbitan', 'maintenance_and_update_frequency', 'update_freq', 'update_frequency')
        dataset.spatial = oneof(package, 'cakupan', 'geographic_coverage', 'spatial', 'spatial_coverage', 'valid_spatial')
        dataset.temporal = oneof(package, 'tahun', 'temporal_coverage', 'temporal_coverage-from', 'temporal_coverage-to', 'temporal_coverage_from', 'temporal_coverage_to', 'time_period_coverage_end', 'time_period_coverage_start', 'valid_from', 'valid_till', 'valid_until')
        dataset.contactPoint = oneof(package, 'maintainer_email', 'author_email', 'contact-email', 'contact_point')
        if package.get('theme-primary'):
            dataset.theme = [package['theme-primary']]

        # Determine the license_id.
        license_id = package.get('license_id')
        if not license_id:
            # License URLs have been found in "licence_url", "licence_url_title" and "access_constraints".
            match = next((value for value in extras.values() if value in licence_url_to_license_id), None)
            if match:
                license_id = licence_url_to_license_id[match]
            elif self.catalog.division_id == 'ocd-division/country:fi':
                license_id = extras.get('licence_url')
            # @note GB ought to clean up its licensing.
            elif self.catalog.division_id == 'ocd-division/country:gb':
                licence = extras.get('licence')
                if licence:
                    if licence in (
                        '["No conditions apply", "None", "Open Government License (OGL)"]',
                        '["No conditions apply", "Open Government License (OGL)", "None"]',
                        '["None", "Open Government License (OGL)"]',
                        'Licence terms and conditions apply (Open Government Licence)',
                        'Open Data available for use under the Open Government Licence',
                        'Open Government Licence',
                        'Open Government Licence, http://www.nationalarchives.gov.uk/doc/open-government-licence',
                        'Open Government Licence, http://www.nationalarchives.gov.uk/doc/open-government-licence/',
                        'Open Government License (http://www.nationalarchives.gov.uk/doc/open-government-licence/)',
                        'Open Government License',
                        'Open Government License.',
                        'Please read Open Government Licence (http://www.nationalarchives.gov.uk/doc/open-government-licence/)',
                        'Use of this data is subject to acceptance of the Open Government Licence',
                    ):
                        license_id = 'uk-ogl'
                    elif licence in (
                        'Contains public sector information licensed under the Open Government Licence v2.0',
                        'Open Government Licence - http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/',
                    ):
                        license_id = 'uk-ogl-2'
                    elif licence in (
                        'This resource is made available under the terms of the Open Government Licence [http://eidchub.ceh.ac.uk/administration-folder/tools/ceh-standard-licence-texts/ceh-open-government-licence/plain]',
                        'Licence conditions apply. This resource is made available under the terms of the Open Government Licence. (http://eidchub.ceh.ac.uk/administration-folder/tools/ceh-standard-licence-texts/ceh-open-government-licence)',
                    ):
                        license_id = 'CEH Open Government Licence'
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
        license_url = extras.get('licence_url') or extras.get('license_url')
        if license_url:
            if package.get('license_url'):
                if license_url != package['license_url'] and not (
                    # @note AU's "licence_url" uses a different, valid URL for "cc-by".
                    self.catalog.division_id == 'ocd-division/country:au' and
                    license_url == 'http://www.opendefinition.org/licenses/cc-by' and
                    package['license_url'] == 'http://creativecommons.org/licenses/by/3.0/au/'
                ) and not (
                    # @note GB's "licence_url" may be less specific than its "license_url".
                    self.catalog.division_id == 'ocd-division/country:gb' and
                    license_url == 'http://www.nationalarchives.gov.uk/doc/open-government-licence/' and
                    package['license_url'] == 'http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/'
                ):
                    self.warning('extras.licence_url expected %s got %s %s' % (package['license_url'], license_url, source_url))
            elif license_id:  # only runs if license_url not previously set
                dataset.license_url = license_url
            else:
                dataset.license_id = license_url
        if extras.get('licence_url_title'):
            if package.get('license_title'):
                if extras['licence_url_title'] != package['license_title']:
                    self.warning('extras.licence_url_title expected %s got %s %s' % (package['license_title'], extras['licence_url_title'], source_url))
            elif license_id:  # only runs if license_title not previously set
                dataset.license_title = extras['licence_url_title']
            else:
                dataset.license_id = extras['licence_url_title']

        try:
            dataset.save()

            for resource in package['resources']:
                distribution = self.find_or_initialize(Distribution, dataset=dataset, _id=resource['id'])
                distribution.json = resource
                distribution.custom_properties = [k for k, v in resource.items() if v and k not in ckan_distribution_properties]
                distribution.division_id = dataset.division_id
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
                if len(dataset.contactPoint) > 254:
                    self.error('dataset.contactPoint is %d' % len(dataset.contactPoint))
                if len(dataset.landingPage) > 500:
                    self.error('dataset.landingPage is %d' % len(dataset.landingPage))
                if len(dataset.license_url) > 200:
                    self.error('dataset.license_url is %d' % len(dataset.license_url))
        except KeyError as e:
            self.error('%s missing key %s' % (source_url, e))


def oneof(d, *keys):
    return next((str(d.get(key)) for key in keys if d.get(key)), '')

# Core CKAN fields.
ckan_dataset_properties = frozenset([
    # package_search retrieves the id and data_dict fields from Solr. The
    # data_dict field is populated with the output of package_show, which
    # respects default_show_package_schema and passes the package through
    # package_dictize... It's easier to just look at the CKAN API output.

    # Modeled
    'author_email',
    'id',
    'isopen',
    'license_id',
    'license_title',
    'license_url',
    'maintainer_email',
    'metadata_created',
    'metadata_modified',
    'name',
    'notes',
    'owner_org',
    'tags',
    'title',
    'type',
    'url',

    # dct:language
    'language',  # AU, CA
    'original_language',  # FI

    # dct:accrualPeriodicity
    'frekuensi_penerbitan',  # ID
    'maintenance_and_update_frequency',  # CA
    'update_freq',  # AU
    'update_frequency',  # EE, FI, GB, PY, UY

    # dct:spatial
    'cakupan',  # ID
    'geographic_coverage',  # GB
    'spatial',  # AU, CA
    'spatial_coverage',  # AU, UY
    'valid_spatial',  # PY

    # dct:temporal
    'tahun',  # ID
    'temporal_coverage',  # UY
    'temporal_coverage-from',  # GB
    'temporal_coverage-to',  # GB
    'temporal_coverage_from',  # AU
    'temporal_coverage_to',  # AU
    'time_period_coverage_end',  # CA
    'time_period_coverage_start',  # CA
    'valid_from',  # FI, PY
    'valid_till',  # FI
    'valid_until',  # PY

    # dcat:contactPoint
    'contact_point',  # AU
    'contact-email',  # EE, GB

    # dcat:theme
    'theme-primary',  # EE, GB

    # Not modeled
    'author',
    'creator_user_id',
    'extras',
    'groups',
    'maintainer',
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
    'version',

    # @see https://github.com/ckan/ckanext-harvest
    'harvest_object_id',
    'harvest_source_id',
    'harvest_source_title',

    # dct:temporal
    'temporal_granularity',  # FI, GB
    'temporal_granularity-other',  # GB
    'geographic_granularity',  # GB
    'geographic_granularity-other',  # GB

    # Boolean
    'core-dataset',  # EE, GB
    'ready_to_publish',  # CA
    'unpublished',  # EE, GB

    # Translations
    # CA
    'attribution_fra',
    'data_series_issue_identification_fra',
    'data_series_name_fra',
    'endpoint_url_fra',
    'keywords_fra',
    'license_title_fra',
    'license_url_fra',
    'notes_fra',
    'title_fra',
    'url_fra',
    # FI
    'copyright_notice_sv',
    'notes_en',
    'notes_sv',
    'title_en',
    'title_sv',
    # TZ
    'title_sw',
    'description_sw',

    # AU
    'data_state',  # "active"

    # EE, GB
    'theme-secondary',  # dct:theme
    'contact-name',  # vcard:fn
    'contact-phone',  # vcard:hasTelephone
    'data_dict',  # JSON as string
    'update_frequency-other',  # set if `update_frequency` is "other"
    'additional_resources',  # resource partition
    'individual_resources',  # resource partition
    'timeseries_resources',  # resource partition
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

    # Translations
    # CA
    'name_fra',
    # FI
    'description_en',
    'description_sv',
    'name_en',
    'name_sv',
    'temporal_granularity_en',
    'update_frequency_en',
])

# Map CKAN properties to model properties.
dataset_properties = {
    'title': 'title',
    'notes': 'description',
    'metadata_created': 'issued',
    'metadata_modified': 'modified',
    'owner_org': 'publisher',
    'id': 'identifier',
    'url': 'landingPage',
    'type': 'type',
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
        'uk-ogl-2',
    'https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/':
        'uk-ogl-2',
    'http://www.naturalengland.org.uk/copyright/default.aspx':
        'Natural England-OS Open Government Licence',
    'http://www.ordnancesurvey.co.uk/docs/licences/os-opendata-licence.pdf':
        'OS OpenData Licence',
    'http://www.ordnancesurvey.co.uk/oswebsite/docs/licences/os-opendata-licence.pdf':
        'OS OpenData Licence',
}

# @see http://www.dati.gov.it/content/infografica
# $('section.module-shallow:eq(1) li a').length = 50
# $('section.module-shallow:eq(1) li a').each(function () { console.log($(this).attr('href').replace('/catalog/dataset?', '').replace('_organization_limit=0', '').replace('organization=', '').replace('&', '')); })
organization_names = [
    # Amministrazioni centrali
    'agid',
    'aifa',
    'inail',
    'inps',
    'istat',
    'mef-ragioneria-generale-dello-stato',
    'ministero-della-salute',
    'ministero-politiche-agricole-alimentari-e-forestali',

    # Amministrazioni regionali
    # 'arpa-umbria',
    # 'autorita-di-bacino-del-fiume-arno',
    # 'commissario-sisma-apuane',
    # 'pat',
    # 'regione-basilicata',
    # 'regione-friuli-venezia-giulia',
    # 'regione-liguria',
    # 'regione-lombardia',
    # 'regione-piemonte',
    # 'regione-sardegna',
    # 'regione-toscana',
    # 'regione-umbria',
    # 'regione-veneto',

    # Amministrazioni provinciali
    # 'provincia-di-lucca',
    # 'provincia-di-pisa',
    # 'provincia-di-prato',
    # 'provincia-di-roma',

    # Communi
    # 'comune-albano-laziale',
    # 'comune-di-bari',
    # 'comune-di-bologna',
    # 'comune-di-catania',
    # 'comune-di-cesena',
    # 'comune-di-firenze',
    # 'comune-di-lecce',
    # 'comune-di-matera',
    # 'comune-di-milano',
    # 'comune-di-napoli',
    # 'comune-di-palermo',
    # 'comune-di-paliano',
    # 'comune-di-pontecorvo',
    # 'comune-di-posta-fibreno',
    # 'comune-di-ravenna',
    # 'comune-di-rignano-flaminio',
    # 'comune-di-rimini',
    # 'comune-di-roma',
    # 'comune-di-roma-agenzia-per-la-mobilita',
    # 'comune-di-torino',
    # 'comune-di-udine',
    # 'comune-di-venezia',
    # 'comune-di-vicenza',

    # Università
    # 'universita-tor-vergata',

    # Miscellaneous
    # 'citta-metropolitana-di-firenze',
]
