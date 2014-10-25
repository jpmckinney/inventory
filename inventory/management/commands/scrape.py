# coding: utf-8

import json
import logging
import re
import signal
import sys
from ast import literal_eval
from multiprocessing import Process
from optparse import make_option
from urllib.parse import urlparse

import ckanapi
import requests
import requests_cache
from django.core.management.base import BaseCommand
from django.db.utils import DataError
from logutils.colorize import ColorizingStreamHandler

from inventory.models import Package, Resource
from inventory.constants import (urls, post_country_codes, ckan_dataset_properties,
                                 ckan_distribution_properties, dataset_properties,
                                 distribution_properties, license_properties,
                                 allowed_package_types, allowed_resource_types)
from inventory.mappings import licence_url_to_license_id


class Handler(ColorizingStreamHandler):
    level_map = {
        logging.DEBUG: (None, 'cyan', False),
        logging.INFO: (None, 'white', False),
        logging.WARNING: (None, 'yellow', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', True),
    }

log = logging.getLogger()  # __name__ to quiet requests


class Command(BaseCommand):
    args = '<country_code country_code ...>'
    help = 'Scrapers packages from CKAN APIs'

    option_list = BaseCommand.option_list + (
        make_option('--no-cache', action='store_false', dest='cache',
                    default=True,
                    help='Do not cache HTTP GET requests.'),
        make_option('--expire-after', action='store', dest='expire_after',
                    type='int',
                    help='The number of seconds after which the cache is expired.'),
        make_option('--exclude', action='store_true', dest='exclude',
                    default=False,
                    help='Exclude the given country codes.'),
        make_option('-n', '--dry-run', action='store_true', dest='dry_run',
                    default=False,
                    help='Print the plan without scraping.'),
        make_option('-q', '--quiet', action='store_const', dest='level',
                    const=logging.INFO,
                    help='Quiet mode. No DEBUG messages.'),
        make_option('--silent', action='store_const', dest='level',
                    const=logging.WARNING,
                    help='Quiet mode. No DEBUG or INFO messages.'),
    )

    python_value_re = re.compile(r"\A\[u'")
    gb_open_license_re = re.compile(r'open government licen[sc]e', re.IGNORECASE)

    def handle(self, *args, **options):
        # @see http://requests-cache.readthedocs.org/en/latest/api.html#requests_cache.core.install_cache
        if options['cache']:
            cache_options = {}
            if options['expire_after']:
                cache_options['expire_after'] = options['expire_after']
            requests_cache.install_cache('inventory_cache', allowable_methods=('HEAD', 'GET', 'POST'), **cache_options)

        log.setLevel(options['level'] or logging.DEBUG)
        handler = Handler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(levelname)-5s %(asctime)s %(message)s', datefmt='%H:%M:%S'))
        log.addHandler(handler)

        if not args or options['exclude']:
            include = dict(urls)
        else:
            include = {}

        if args:
            if options['exclude']:
                for arg in args:
                    del include[arg]
            else:
                for country_code, url in urls:
                    if country_code in args:
                        include[country_code] = url

        for country_code, url in include.items():
            print('{}: {}'.format(country_code, url))

        if options['dry_run']:
            exit(0)

        processes = [
            Process(target=self.scrape, args=(country_code, url))
            for country_code, url in include.items()
        ]

        def signal_handler(signal, frame):
            for process in processes:
                process.terminate()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        for process in processes:
            process.start()

        for process in processes:
            process.join()

    def scrape(self, country_code, url):
        log.info(url)

        # Get the base CKAN URL.
        # @note MD's URL rewriting omits query string parameters.
        parsed = urlparse(url)
        if not parsed.path or parsed.path == '/':
            test_url = '%s://%s/api/3/action/package_list' % (parsed.scheme, parsed.netloc)
            try:
                response = requests.head(test_url)
                if response.status_code in (301, 302):
                    location = urlparse(response.headers['Location'].replace('/api/3/action/package_list', ''))
                    if not location.scheme and not location.netloc:
                        url = '%s://%s%s' % (parsed.scheme, parsed.netloc, location.path)
            except requests.packages.urllib3.exceptions.ProtocolError:
                log.error('ProtocolError %s' % test_url)

        # Create a CKAN client.
        client = ckanapi.RemoteCKAN(url, get_only=country_code not in post_country_codes)  # GET so we can cache
        try:
            response = client.action.package_search(rows=300000)  # the most datasets in any catalog
        except (ckanapi.errors.CKANAPIError, ckanapi.errors.ServerIncompatibleError):
            log.error('May not be CKAN %s' % url)
            return
        except requests.packages.urllib3.exceptions.ProtocolError:
            log.error('ProtocolError %s package_search' % url)
            return

        packages = response['results']
        expected = response['count']
        actual = len(packages)

        # Get all the packages.
        if expected == actual:
            log.info('%d packages %s' % (actual, url))
        else:
            try:
                package_list = client.action.package_list()
            except requests.packages.urllib3.exceptions.ProtocolError:
                log.error('ProtocolError %s package_list' % url)
                return

            # @note US redirects package_list to to package_search.
            if isinstance(package_list, dict):  # package_search
                expected = package_list['count']
            else:
                expected = len(package_list)

            # @note AR over-reports the 'count' in package_search.
            if expected == actual:
                log.info('%d packages %s' % (actual, url))
            else:
                log.info('%d packages %s' % (expected, url))

                start = actual
                while response['results']:
                    print('.', end='', flush=True)

                    try:
                        response = client.action.package_search(rows=actual, start=start)
                    except ckanapi.errors.CKANAPIError:
                        log.error('CKANAPIError %sapi/3/action/package_search?rows=%d&start=%d' % (url, actual, start))
                    except requests.packages.urllib3.exceptions.ProtocolError:
                        log.error('ProtocolError %sapi/3/action/package_search?rows=%d&start=%d' % (url, actual, start))

                    packages += response['results']
                    start += len(response['results'])

        # Process the packages.
        for package in packages:  # dcat:Dataset
            # GB lists packages for which no data is published.
            if country_code == 'gb' and package.get('unpublished') == 'true':
                continue

            source_url = '%sapi/3/action/package_show?id=%s' % (url, package['name'])

            extras = {}

            # Try to make values uniform for use below.
            for extra in package.get('extras', []):
                value = extra['value']

                if isinstance(value, str):
                    if self.python_value_re.match(value):
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
            if country_code == 'gb' and not (
                package.get('license_id') == 'uk-ogl' or
                bool(self.gb_open_license_re.search(extras.get('licence', ''))) or
                bool(self.gb_open_license_re.search(extras.get('licence_url_title', '')))
            ):
                continue

            options = {
                'country_code': country_code,
                'name': package['name'],
            }
            try:
                record = Package.objects.get(**options)
            except Package.DoesNotExist:
                record = Package(**options)

            record.source_url = source_url
            record.json = package
            record.custom_properties = list(package.keys() - ckan_dataset_properties)
            record.extras_keys = list(set(extras.keys()))

            for dataset_property, column_name in dataset_properties.items():
                if package.get(dataset_property):
                    setattr(record, column_name, package[dataset_property])
            for license_property in license_properties:
                if package.get(license_property):
                    setattr(record, license_property, package[license_property])

            try:
                # Some quick validations.
                if package.get('private'):
                    log.warning('private %s' % source_url)
                if package['state'] != 'active':
                    log.warning('unknown state "%s" %s' % (package['state'], source_url))
                if package['type'] and package['type'] not in allowed_package_types:
                    log.warning('unknown type "%s" %s' % (package['type'], source_url))

                # Determine the license_id.
                license_id = package.get('license_id')
                if not license_id:
                    # License URLs have been found in "licence_url", "licence_url_title" and "access_constraints".
                    match = next((value for value in extras.values() if value in licence_url_to_license_id), None)
                    if match:
                        license_id = licence_url_to_license_id[match]
                    elif country_code == 'gb' and extras.get('licence') == 'Open Government Licence':
                        license_id = 'uk-ogl'
                    if package.get('license_title') or package.get('license_url'):
                        log.warning('license_title or license_url but no license_id %s' % source_url)

                if license_id:
                    record.license_id = license_id

                # The top-level "license_url" and "license_title" should agree
                # with the extra "licence_url" and "licence_url_title".
                if extras.get('licence_url'):
                    if package.get('license_url'):
                        if extras.get('licence_url') != package.get('license_url') and (
                            country_code != 'au' or
                            # @note AU's "licence_url" uses a different URL for "cc-by".
                            package.get('license_url') != 'http://creativecommons.org/licenses/by/3.0/au/' or
                            extras.get('licence_url') != 'http://www.opendefinition.org/licenses/cc-by'
                        ):
                            log.warning('extras.licence_url expected %s got %s' % (package.get('license_url'), extras.get('licence_url')))
                    elif license_id:  # only runs if license_url not previously set
                        record.license_url = extras.get('licence_url')
                    else:
                        log.warning('extras.licence_url but no license_id %s' % source_url)
                if extras.get('licence_url_title'):
                    if package.get('license_title'):
                        if extras.get('licence_url_title') != package.get('license_title'):
                            log.warning('extras.licence_url_title expected %s got %s' % (package.get('license_title'), extras.get('licence_url_title')))
                    elif license_id:  # only runs if license_title not previously set
                        record.license_title = extras.get('licence_url_title')
                    else:
                        log.warning('extras.licence_url_title but no license_id %s' % source_url)

                record.save()

                for resource in package['resources']:  # dcat:Distribution
                    if resource.get('state') and resource['state'] != 'active':
                        log.warning('unknown status "%s" %d' % (resource['state'], source_url, resource['position']))
                    if resource.get('resource_type') and resource['resource_type'] not in allowed_resource_types:
                        log.warning('unknwon resource_type "%s" %s %d' % (resource['resource_type'], source_url, resource['position']))

                    options = {
                        'package': record,
                        '_id': resource['id'],
                    }
                    try:
                        subrecord = Resource.objects.get(**options)
                    except Resource.DoesNotExist:
                        subrecord = Resource(**options)

                    subrecord.json = resource
                    subrecord.custom_properties = list(resource.keys() - ckan_distribution_properties)

                    for distribution_property, column_name in distribution_properties.items():
                        if resource.get(distribution_property):
                            setattr(subrecord, column_name, resource[distribution_property])

                    subrecord.save()

            except DataError as e:
                try:
                    if len(subrecord.url) > 600:
                        log.error('subrecord.url is %d' % len(subrecord.url))
                except NameError:
                    if len(record.source_url) > 200:
                        log.error('record.source_url is %d' % len(record.source_url))
                    if len(record.url) > 500:
                        log.error('record.url is %d' % len(record.url))
                    if len(record.license_url) > 200:
                        log.error('record.license_url is %d' % len(record.license_url))
                    if len(record.maintainer_email) > 254:
                        log.error('record.maintainer_email is %d' % len(record.maintainer_email))
                    if len(record.author_email) > 254:
                        log.error('record.author_email is %d' % len(record.author_email))
            except KeyError as e:
                log.error('%s missing key %s' % (source_url, e))

        log.info('%s done' % country_code)
