# coding: utf-8

import json
import logging
import os
import re
import signal
import sys
from collections import defaultdict
from multiprocessing import Process
from urllib.parse import urlparse

import ckanapi
import requests
import requests_cache
from logutils.colorize import ColorizingStreamHandler

from constants import (urls, post_country_codes, ckan_dataset_properties,
    ckan_distribution_properties, dataset_properties, distribution_properties,
    license_properties, license_extra_properties, allowed_package_types,
    allowed_resource_types)
from mappings import licence_url_to_license_id

requests_cache.install_cache('inventory_cache')  # will never expire unless expire_after is set

class Handler(ColorizingStreamHandler):
    level_map = {
        logging.DEBUG: (None, 'cyan', False),
        logging.INFO: (None, 'white', False),
        logging.WARNING: (None, 'yellow', False),
        logging.ERROR: (None, 'red', False),
        logging.CRITICAL: ('red', 'white', True),
    }

# log = logging.getLogger('inventory')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = Handler(sys.stdout)
handler.setFormatter(logging.Formatter('%(levelname)-5s %(asctime)s %(message)s', datefmt='%H:%M:%S'))
log.addHandler(handler)

# Some catalogs use English license titles at first and translate later.
default_license_metadata = {
    'notspecified': {
        'license_title': 'License Not Specified',
    },
    'odc-odbl': {
        'license_title': 'Open Data Commons Open Database License (ODbL)',
    },
    'other-open': {
        'license_title': 'Other (Open)',
    },
    'uk-ogl': {
        'license_title': 'UK Open Government Licence (OGL)',
        'license_url': 'http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/',
    }
}

gb_open_license_re = re.compile(r'open government licen[sc]e', re.IGNORECASE)

def scrape(country_code, url):
    log.info(url)

    dataset_custom_properties = set()
    distribution_custom_properties = set()
    license_metadata = defaultdict(dict)
    licenses = defaultdict(int)
    formats = defaultdict(int)
    dataset_metadata = defaultdict(int)
    distribution_metadata = defaultdict(int)

    # Collect unique "extras.key" for later inspection.
    dataset_metadata['extras'] = set()

    # MD's URL rewriting omits query string parameters.
    parsed = urlparse(url)
    if not parsed.path or parsed.path == '/':
        test_url = "%s://%s/api/3/action/package_list" % (parsed.scheme, parsed.netloc)
        try:
            response = requests.head(test_url)
            if response.status_code in (301, 302):
                location = urlparse(response.headers['Location'].replace('/api/3/action/package_list', ''))
                if not location.scheme and not location.netloc:
                    url = "%s://%s%s" % (parsed.scheme, parsed.netloc, location.path)
        except requests.packages.urllib3.exceptions.ProtocolError:
            log.error("protocol error %s" % test_url)

    client = ckanapi.RemoteCKAN(url, get_only=country_code not in post_country_codes)  # GET so we can cache
    try:
        response = client.action.package_search(rows=300000)
    except (ckanapi.errors.CKANAPIError, ckanapi.errors.ServerIncompatibleError):
        log.error("may not be CKAN %s" % url)
        return
    except requests.packages.urllib3.exceptions.ProtocolError:
        log.error("protocol error %s package_search" % url)
        return

    packages = response['results']
    expected = response['count']
    actual = len(packages)

    if expected == actual:
        log.info("%d packages %s" % (actual, url))
    else:
        try:
            package_list = client.action.package_list()
        except requests.packages.urllib3.exceptions.ProtocolError:
            log.error("network error %s package_list" % url)
            return

        # US redirects package_list to to package_search.
        if isinstance(package_list, dict):
            expected = package_list['count']
        else:
            expected = len(package_list)

        # AR over-reports the 'count' in package_search.
        if expected == actual:
            log.info("%d packages %s" % (actual, url))
        else:
            log.info("%d packages %s" % (expected, url))

            start = actual
            while response['results']:
                print('.', end='', flush=True)

                try:
                    response = client.action.package_search(rows=actual, start=start)
                except ckanapi.errors.CKANAPIError:
                    log.error('CKAN error %sapi/3/action/package_search?rows=%d&start=%d' % (url, actual, start))
                except requests.packages.urllib3.exceptions.ProtocolError:
                    log.error('protocol error %sapi/3/action/package_search?rows=%d&start=%d' % (url, actual, start))

                packages += response['results']
                start += len(response['results'])

    for package in packages:
        extras = {}

        for extra in package.get('extras', []):
            value = extra['value']
            # Try to make the values uniform. GB's "theme-secondary" has values
            # like "[u'Defence', u'Government']" which are Python, not JSON.
            if value.startswith('[') and extra['key'] != 'theme-secondary':
                try:
                    value = json.loads(value)
                    if len(value) == 1:
                        value = value[0]
                        # Value must be hashable.
                        if not isinstance(value, str):
                            value = json.dumps(value)
                    else:
                        value = extra['value']
                except ValueError as e:
                    log.error("%s %s %sapi/3/action/package_show?id=%s" % (e, value, url, package['name']))
            if extra['key'] in extras:
                log.warning("multiple %s %sapi/3/action/package_show?id=%s" % (extra['key'], url, package['name']))
            else:
                extras[extra['key']] = value

        dataset_metadata['extras'] |= extras.keys()

        if country_code == 'gb':
            if package.get('unpublished') == 'true':
                continue
            # @see https://github.com/datagovuk/ckanext-dgu/blob/8b48fc88c9be8f3b5e3738ea96c9baab1a7deef0/ckanext/dgu/search_indexing.py#L71
            if not (package.get('license_id') == 'uk-ogl' or
                    bool(gb_open_license_re.search(extras.get('licence', ''))) or
                    bool(gb_open_license_re.search(extras.get('licence_url_title', '')))):
                continue

        try:
            if package.get('private'):
                log.warning("private %sapi/3/action/package_show?id=%s" % (url, package['name']))
            if package['state'] != 'active':
                log.warning("not active %sapi/3/action/package_show?id=%s" % (url, package['name']))
            if package['type'] and package['type'] not in allowed_package_types:
                log.warning("type '%s' %sapi/3/action/package_show?id=%s" % (package['type'], url, package['name']))

            for dataset_property in dataset_properties:
                if package.get(dataset_property):
                    dataset_metadata[dataset_property] += 1

            dataset_custom_properties |= package.keys() - ckan_dataset_properties

            license_id = package.get('license_id')
            if license_id:
                licenses[license_id] += 1
                for license_property in license_properties:
                    actual = package.get(license_property)
                    if actual:
                        expected = license_metadata[license_id].get(license_property)
                        if expected:
                            if actual not in (expected, license_id, default_license_metadata.get(license_id, {}).get(license_property)):
                                log.warning("%s for %s expected %s got %s" % (license_property, license_id, expected, actual))
                        else:
                            license_metadata[license_id][license_property] = actual
            elif package.get('license_title') or package.get('license_url'):
                log.warning("license_title or license_url but no license_id %sapi/3/action/package_show?id=%s" % (url, package['name']))

            # Try to avoid a null license_id.
            if not license_id:
                # License URLs have been found in licence_url, licence_url_title and access_constraints.
                match = next((value for value in extras.values() if value in licence_url_to_license_id), None)
                if match:
                    license_id = licence_url_to_license_id[match]
                    licenses[license_id] += 1
                elif country_code == 'gb' and extras.get('licence') == 'Open Government Licence':
                    license_id = 'uk-ogl'
                    licenses[license_id] += 1

            # The top-level "license_url" and "license_title" should
            # agree with the extra "licence_url" and "licence_url_title".
            # AU's "licence_url" uses a different URL for "cc-by":
            # "http://www.opendefinition.org/licenses/cc-by".
            if extras.get('licence_url'):
                if package.get('license_url'):
                    if extras.get('licence_url') not in (package.get('license_url'), 'http://www.opendefinition.org/licenses/cc-by'):
                        log.warning("extras.licence_url expected %s got %s" % (package.get('license_url'), extras.get('licence_url')))
                elif license_id:
                    license_metadata[license_id]['license_url'] = extras.get('licence_url')
                else:
                    log.warning("extras.licence_url but no license_id %sapi/3/action/package_show?id=%s" % (url, package['name']))

            if extras.get('licence_url_title'):
                if package.get('license_title'):
                    if extras.get('licence_url_title') != package.get('license_title'):
                        log.warning("extras.licence_url_title expected %s got %s" % (package.get('license_title'), extras.get('licence_url_title')))
                elif license_id:
                    license_metadata[license_id]['license_title'] = extras.get('licence_url_title')
                else:
                    log.warning("extras.licence_url_title but no license_id %sapi/3/action/package_show?id=%s" % (url, package['name']))

            # Count each format only once to get a sense of the popularity of formats.
            distribution_formats_found = set()
            distribution_properties_found = set()
            for resource in package['resources']:  # dcat:Distribution
                if resource.get('state') and resource['state'] != 'active':
                    log.warning("not active %sapi/3/action/package_show?id=%s %d" % (url, package['name'], resource['position']))
                if resource.get('resource_type') and resource['resource_type'] not in allowed_resource_types:
                    log.warning("resource_type '%s' %sapi/3/action/package_show?id=%s %d" % (resource['resource_type'], url, package['name'], resource['position']))

                for distribution_property in distribution_properties:
                    if resource.get(distribution_property):
                        distribution_properties_found.add(distribution_property)

                distribution_custom_properties |= resource.keys() - ckan_distribution_properties

                # Not sure why catalogs sometimes omit the mimetype for the same format.
                # @todo Need to normalize mimetype/format here, otherwise may double count.
                distribution_format = resource.get('mimetype') or resource['format']
                if distribution_format:
                    distribution_formats_found.add(distribution_format)

            for distribution_format in distribution_formats_found:
                formats[distribution_format] += 1
            for distribution_property in distribution_properties_found:
                distribution_metadata[distribution_property] += 1

        except KeyError as e:
            log.error("%sapi/3/action/package_show?id=%s missing key %s" % (url, package['name'], e))

    # set() is not JSON serializable.
    dataset_metadata['extras'] = list(dataset_metadata['extras'])

    with open('out/ckan/%s.licenses.json' % country_code, 'w') as f:
        json.dump(licenses, f)
    with open('out/ckan/%s.formats.json' % country_code, 'w') as f:
        json.dump(formats, f)
    with open('out/ckan/%s.metadata_dataset.json' % country_code, 'w') as f:
        json.dump(dataset_metadata, f)
    with open('out/ckan/%s.metadata_distribution.json' % country_code, 'w') as f:
        json.dump(distribution_metadata, f)
    with open('out/ckan/%s.custom_dataset.json' % country_code, 'w') as f:
        json.dump(list(dataset_custom_properties), f)
    with open('out/ckan/%s.custom_distribution.json' % country_code, 'w') as f:
        json.dump(list(distribution_custom_properties), f)
    with open('out/ckan/%s.metadata_license.json' % country_code, 'w') as f:
        json.dump(license_metadata, f)
    log.info("%s done" % country_code)

if __name__ == '__main__':
    processes = [Process(target=scrape, args=(country_code, url)) for country_code, url in urls]

    def signal_handler(signal, frame):
        for process in processes:
            process.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    for process in processes:
        process.start()

    for process in processes:
        process.join()
