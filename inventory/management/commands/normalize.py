from .base import InventoryCommand
from inventory.models import Dataset


class Command(InventoryCommand):
    def handle(self, *args, **options):
        qs = Dataset.objects.filter(license='')

        # UK and RO use the same license ID for different licenses.
        qs.filter(country_code='gb', license_id='uk-ogl').update(license='http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/')
        qs.filter(country_code='ro', license_id='uk-ogl').update(license='http://data.gov.ro/base/images/logoinst/OGL-ROU-1.0.pdf')

        license_ids = {
            # Against DRM
            'against-drm': 'http://www.freecreations.org/Against_DRM2.html',
            # Creative Commons
            'cc-by-4': 'http://creativecommons.org/licenses/by/4.0/',
            'cc-zero': 'http://creativecommons.org/publicdomain/zero/1.0/',
            'cc0': 'http://creativecommons.org/publicdomain/zero/1.0/',
            'creative-commons-attribution-cc-by-': 'http://creativecommons.org/licenses/by/3.0/nl/',
            'naamsvermelding---gelijkdelen-cc-by-sa-': 'http://creativecommons.org/licenses/by-sa/3.0/nl/',
            # Open Data Commons
            'odc-by': 'http://opendatacommons.org/licenses/by/1.0/',
            'odc-odbl': 'http://opendatacommons.org/licenses/odbl/1.0/',
            'odc-pddl': 'http://opendatacommons.org/licenses/pddl/1.0/',

            # Imprecise
            'Attribution (CC-BY)': 'http://creativecommons.org/licenses/by/',
            'Attribution-Share Alike (BY-SA)': 'http://creativecommons.org/licenses/by-sa/',

            # CA
            'ca-ogl-lgo': 'http://data.gc.ca/eng/open-government-licence-canada',
            'ca-odla-aldg': 'http://ocl-cal.gc.ca/eic/site/012.nsf/eng/00873.html',
            # GB
            'Natural England-OS Open Government Licence': 'http://webarchive.nationalarchives.gov.uk/20140605090108/http://www.naturalengland.org.uk/copyright/default.aspx',
            'OS OpenData Licence': 'http://www.ordnancesurvey.co.uk/docs/licences/os-opendata-licence.pdf',
            'uk-citation-required': 'http://example.com/uk-citation-required',  # No URL
            # IE
            'gov-copyright': 'http://www.irishstatutebook.ie/2000/en/act/pub/0028/sec0191.html#sec191',
            'marine': 'http://www.marine.ie/NR/rdonlyres/6F56279C-631D-42AC-B495-74C76CE93A8B/0/MIDataLicenseMar2013.pdf',
            'psi': 'http://psi.gov.ie/files/2010/03/PSI-Licence.pdf',
            # IT
            'iodl1': 'http://www.formez.it/iodl/',
            'iodl2': 'http://www.dati.gov.it/iodl/2.0/',
            # NL
            'publiek-domein': 'http://example.com/public-domain',  # No URL
            # UY
            'odc-uy': 'http://example.com/odc-uy',  # No URL

            # Generic
            'notspec': 'http://example.com/unknown',
            'notspecified': 'http://example.com/unknown',
            'other-at': 'http://example.com/unknown',
            'other-closed': 'http://example.com/unknown',
            'other-nc': 'http://example.com/unknown',
            'other-open': 'http://example.com/unknown',
            'other-pd': 'http://example.com/unknown',
        }
        for license_id, license in license_ids.items():
            qs.filter(license_id=license_id).update(license=license)

        license_urls = {
            'http://creativecommons.org/licenses/by/3.0/au/': 'http://creativecommons.org/licenses/by/3.0/au/',
            'http://creativecommons.org/licenses/by-nc/2.0/': 'http://creativecommons.org/licenses/by-nc/2.0/',
            # Imprecise
            'http://www.opendefinition.org/licenses/cc-by': 'http://creativecommons.org/licenses/by/',
            'http://www.opendefinition.org/licenses/cc-by-sa': 'http://creativecommons.org/licenses/by-sa/',
            'http://creativecommons.org/licenses/by-nc-nd/': 'http://creativecommons.org/licenses/by-nc-nd/',
            'http://creativecommons.org/licenses/by-nc-sa': 'http://creativecommons.org/licenses/by-nc-sa/',
            'http://creativecommons.org/licenses/by-nd/': 'http://creativecommons.org/licenses/by-nd/',
        }
        for license_url, license in license_urls.items():
            qs.filter(license_url=license_url).update(license=license)

        license_titles = {
            'cc-nc': 'http://creativecommons.org/licenses/nc/1.0/',
            # Imprecise
            'cc-by': 'http://creativecommons.org/licenses/by/',
            'cc-by-nd': 'http://creativecommons.org/licenses/by-nd/',
            'cc-by-sa': 'http://creativecommons.org/licenses/by-sa/',
            # Generic
            'License Not Specified': 'http://example.com/unknown',
        }
        for license_title, license in license_titles.items():
            qs.filter(license_title=license_title).update(license=license)
