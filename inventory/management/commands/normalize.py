import mimetypes
import re
from collections import OrderedDict
from optparse import make_option

from . import InventoryCommand
from inventory.models import Dataset, Distribution

mimetypes.init()


class Command(InventoryCommand):
    help = 'Normalizes property values'

    option_list = InventoryCommand.option_list + (
        make_option('--licenses', action='store_true', dest='licenses',
                    default=False,
                    help='Normalize licenses.'),
        make_option('--media-types', action='store_true', dest='media_types',
                    default=False,
                    help='Normalize media types.'),
    )

    def handle(self, *args, **options):
        self.setup(*args, **options)

        if args:
            criteria = {'country_code__in': [catalog.country_code for catalog in self.catalogs]}
        else:
            criteria = {}

        if options['media_types']:
            self.info('Normalizing media types...')
            kwargs = criteria.copy()
            kwargs['mediaType'] = ''
            qs = Distribution.objects.filter(**kwargs)

            for media_type, extension in types:
                if not mimetypes.types_map.get(extension):
                    mimetypes.add_type(media_type, extension)

            self.warnings = {}
            self.warnings_count = 0

            # @todo mimetype_inner (br, uy, it): Distribution.objects.exclude(mimetype_inner='').count()
            for distribution in qs:
                self.save = True

                guesses = {
                    'mimetype': '',
                    'format': '',
                    'accessURL': '',
                }

                # Make the guesses.
                if distribution.mimetype:
                    guesses['mimetype'] = self.guess_type(distribution.mimetype)
                if distribution.format:
                    guesses['format'] = self.guess_type(distribution.format)
                if distribution.accessURL:
                    guess = mimetypes.guess_type(distribution.accessURL)
                    if guess[1] == 'gzip' and (guesses['mimetype'] and guesses['mimetype'] != guess[0] or guesses['format'] and guesses['format'] != guess[0]):
                        guesses['accessURL'] = 'application/gzip'
                    else:
                        guesses['accessURL'] = guess[0] or ''

                # Eliminate non-media types.
                for field, media_type in guesses.items():
                    if not media_type or self.ignore_type(media_type):
                        guesses[field] = ''

                # Eliminate empty media types.
                media_types = list(filter(None, guesses.values()))

                # Media types guessed from extensions, e.g. "application/xml",
                # can be less specific than e.g. "application/rdf+xml".
                specific_media_type = None
                for ambiguous_media_type, specific_media_types in ambiguous_media_types.items():
                    # If the media types include an ambiguous media type and a
                    # specific media type, eliminate the ambigious media type.
                    if ambiguous_media_type in media_types:
                        specific_media_type = next((media_type for media_type in media_types if media_type in specific_media_types), None)
                        if specific_media_type:
                            media_types = [media_type for media_type in media_types if media_type != ambiguous_media_type]
                            break

                # Test if the guesses agree with each other.
                if specific_media_type:
                    if len(set(media_types)) > 1:
                        self.bad_guess('Multiple specific media types', guesses, distribution)
                elif guesses['accessURL']:
                    # @todo Do HEAD requests, as sometimes the file extension
                    # is misleading, e.g. .xml redirects to .html in GB. Note
                    # that even when the metadata is consistent, the media type
                    # could be incorrect.
                    if guesses['mimetype'] and guesses['accessURL'] != guesses['mimetype']:
                        self.bad_guess('Conflict', guesses, distribution)
                    elif guesses['format'] and guesses['accessURL'] != guesses['format']:
                        self.bad_guess('Conflict', guesses, distribution)
                elif guesses['mimetype'] and guesses['format'] and guesses['mimetype'] != guesses['format']:
                    self.bad_guess('Conflict', guesses, distribution)

                # Test that we recognize the media types.
                for media_type in media_types:
                    if media_type and not self.valid_type(media_type):
                        self.bad_guess('Unrecognized', guesses, distribution)

                # If a unique media type is recognized.
                if self.save and len(set(media_types)) == 1:
                    distribution.mediaType = media_types[0]
                    distribution.save()

            for key, (sample, count) in sorted(self.warnings.items(), key=lambda warning: warning[1][1]):
                message, guesses = list(key)
                guesses = dict(guesses)

                print('{:5} {}'.format(count, message))
                for field in ('mimetype', 'format', 'accessURL'):
                    value = getattr(sample, field)
                    if value:
                        if field == 'accessURL' and len(value) > 120:
                            value = '{}..{}'.format(value[:59], value[-59:])
                        # e.g. "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        print('  {:9} {:73} {}'.format(field, guesses[field], value))
                print()

            print('Warnings: {}/{} ({} unique)'.format(self.warnings_count, qs.count(), len(self.warnings)))

        if options['licenses']:
            self.info('Normalizing licenses...')
            kwargs = criteria.copy()
            kwargs['license'] = ''
            qs = Dataset.objects.filter(**kwargs)

            # MD http://data.gov.md/ro/termeni-si-conditii
            # MD doesn't take advantage of CKAN's per-dataset licensing.
            # qs = Dataset.objects.filter(country_code='md'); qs.filter(license_id='notspecified').count() / qs.count()
            qs.filter(country_code='md', license_id='notspecified').update(license='http://data.gov.md/en/terms-and-conditions')
            # MX displays "Libro Uso MX" for all datasets.
            # cc-by http://catalogo.datos.gob.mx/dataset/mexico-prospero-estadisticas-nacionales
            # notspecified http://catalogo.datos.gob.mx/dataset/niveles-actuales-de-rios
            qs.filter(country_code='mx', license_id__in=('cc-by', 'notspecified', '')).update(license='http://datos.gob.mx/libreusomx/')

            # ID http://data.id/lisensi-dan-atribusi.html
            qs.filter(country_code='id', license_id='cc-by').update(license='http://creativecommons.org/licenses/by/4.0/')
            # IT http://www.dati.gov.it/content/note-legali
            qs.filter(country_code='it', license_id='cc-by').update(license='http://creativecommons.org/licenses/by/3.0/it/')

            # UK and RO use the same license ID for different licenses.
            qs.filter(country_code='gb', license_id='uk-ogl').update(license='http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/')
            qs.filter(country_code='ro', license_id='uk-ogl').update(license='http://data.gov.ro/base/images/logoinst/OGL-ROU-1.0.pdf')

            for license_id, license in license_ids.items():
                qs.filter(license_id=license_id).update(license=license)
            for license_url, license in license_urls.items():
                qs.filter(license_url=license_url).update(license=license)
            for license_title, license in license_titles.items():
                qs.filter(license_title=license_title).update(license=license)

    def guess_type(self, value):
        value = re.sub('\A\.', '', ' '.join(value.lower().split()))  # Normalize case and spaces and remove period from extension.
        value = format_corrections.get(value, value)
        if not self.valid_type(value):
            value = mimetypes.types_map.get('.{}'.format(value), value)
        return value

    def valid_type(self, value):
        return value in mimetypes.types_map.values() or value in valid_media_types

    def ignore_type(self, value):
        return value in ignore_media_types or ',' in value

    def bad_guess(self, message, guesses, sample):
        self.save = False
        key = (message, tuple(guesses.items()))
        if not self.warnings.get(key):
            self.warnings[key] = [sample, 1]
        else:
            value = self.warnings[key]
            self.warnings[key] = [value[0], value[1] + 1]
        self.warnings_count += 1


license_ids = {
    # Against DRM
    'against-drm': 'http://www.freecreations.org/Against_DRM2.html',
    # Creative Commons
    'cc-by-4':                                 'http://creativecommons.org/licenses/by/4.0/',
    'cc-zero':                                 'http://creativecommons.org/publicdomain/zero/1.0/',
    'cc0':                                     'http://creativecommons.org/publicdomain/zero/1.0/',
    'creative-commons-attribution-cc-by-':     'http://creativecommons.org/licenses/by/3.0/nl/',
    'naamsvermelding---gelijkdelen-cc-by-sa-': 'http://creativecommons.org/licenses/by-sa/3.0/nl/',
    'Creative Commons 1.0 Universal (http://creativecommons.org/publicdomain/zero/1.0/legalcode)': 'http://creativecommons.org/publicdomain/zero/1.0/',
    # NL https://data.overheid.nl/data/
    'publiek-domein':                          'http://creativecommons.org/publicdomain/mark/1.0/',
    # PH confirmed via email
    'Attribution (CC-BY)':                     'http://creativecommons.org/licenses/by/3.0/ph/',
    'Attribution-Share Alike (BY-SA)':         'http://creativecommons.org/licenses/by-sa/',
    # Open Data Commons
    'odc-by':   'http://opendatacommons.org/licenses/by/1.0/',
    'odc-odbl': 'http://opendatacommons.org/licenses/odbl/1.0/',
    'odc-pddl': 'http://opendatacommons.org/licenses/pddl/1.0/',

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
    # UY
    # https://catalogodatos.gub.uy/
    'odc-uy': 'http://datos.gub.uy/wps/wcm/connect/856cc1804db0463baa8bea01b72d8394/terminos-catalogodatos.pdf?MOD=AJPERES&ContentCache=NONE&CACHEID=856cc1804db0463baa8bea01b72d8394',

    # Generic
    'No license provided': 'http://example.com/notspecified',
    'notspec':             'http://example.com/notspecified',
    'notspecified':        'http://example.com/notspecified',
    'other-at':            'http://example.com/other-at',
    'other-closed':        'http://example.com/other-closed',
    'other-nc':            'http://example.com/other-nc',
    'other-open':          'http://example.com/other-open',
    'other-pd':            'http://example.com/other-pd',
    'Public Domain':       'http://example.com/other-pd',
}
license_urls = {
    # Identical
    'http://creativecommons.org/licenses/by/3.0/au/':  'http://creativecommons.org/licenses/by/3.0/au/',
    'http://creativecommons.org/licenses/by-nc/2.0/':  'http://creativecommons.org/licenses/by-nc/2.0/',
    'http://creativecommons.org/licenses/by-nc-nd/':   'http://creativecommons.org/licenses/by-nc-nd/',
    'http://creativecommons.org/licenses/by-nc-sa':    'http://creativecommons.org/licenses/by-nc-sa/',
    'http://creativecommons.org/licenses/by-nd/':      'http://creativecommons.org/licenses/by-nd/',
    # Correction
    'http://www.opendefinition.org/licenses/cc-by':    'http://creativecommons.org/licenses/by/',
    'http://www.opendefinition.org/licenses/cc-by-sa': 'http://creativecommons.org/licenses/by-sa/',
}
license_titles = {
    'cc-nc':    'http://creativecommons.org/licenses/nc/1.0/',
    # Imprecise
    'cc-by':    'http://creativecommons.org/licenses/by/',
    'cc-by-nd': 'http://creativecommons.org/licenses/by-nd/',
    'cc-by-sa': 'http://creativecommons.org/licenses/by-sa/',
    # Generic
    'License Not Specified': 'http://example.com/notspecified',
}


# Additional media types.
types = (
    # http://reference.wolfram.com/language/ref/format/DBF.html
    ('application/dbf', '.dbf'),

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc6713#section-3
    ('application/gzip', '.gz'),

    # http://tools.ietf.org/html/draft-hallambaker-jsonl-01
    ('application/json-l', '.jsonl'),

    # https://tools.ietf.org/html/rfc2220
    ('application/marc', 'marc'),

    # http://blogs.msdn.com/b/jaimer/archive/2008/01/04/mime-types.aspx
    ('application/msaccess', '.accdb'),

    # http://www.w3.org/TR/n-triples/#n-triples-mediatype
    ('application/n-triples', '.nt'),

    # http://www.w3.org/TR/owl2-xml-serialization/#Appendix:_Internet_Media_Type.2C_File_Extension.2C_and_Macintosh_File_Type
    ('application/owl+xml', '.owl'),

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc3870
    ('application/rdf+xml', '.rdf'),

    # http://www.w3.org/TR/2013/REC-rdf-sparql-XMLres-20130321/#mime
    ('application/sparql-results+xml', '.srx'),

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    ('application/vnd.geo+json', '.geojson'),

    # http://www.w3.org/TR/wsdl20/#ietf-draft
    ('application/wsdl+xml', '.wsdl'),

    # http://blogs.msdn.com/b/jaimer/archive/2008/01/04/mime-types.aspx
    ('application/x-msaccess', '.mdb'),

    # http://en.wikipedia.org/wiki/Torrent_file
    ('application/x-bittorrent', '.torrent'),

    # http://en.wikipedia.org/wiki/Proxy_auto-config
    ('application/x-ns-proxy-autoconfig', '.pac'),

    ('application/x-spss-sav', '.sav'),

    # http://support.sas.com/resources/papers/proceedings13/115-2013.pdf
    ('application/x-sas', '.sas'),

    # http://inspire.ec.europa.eu/media-types/
    ('application/x-ascii-grid', '.grd'),
    ('application/x-filegdb', '.gdb'),
    ('application/x-worldfile', '.tfw'),

    # https://github.com/qgis/QGIS/blob/master/debian/mime/application
    ('application/x-esri-crs', '.prj'),
    ('application/x-esri-shape', '.shx'),
    ('application/x-mapinfo-mif', '.mif'),
    ('application/x-qgis-project', '.qgs'),
    ('application/x-raster-ecw', '.ecw'),

    # http://reference.wolfram.com/language/ref/format/LWO.html
    ('image/x-lwo', '.lwo'),
)

ambiguous_media_types = {
    'application/json': [
        'application/vnd.geo+json',
    ],
    'application/xml': [
        'application/atom+xml',
        'application/gml+xml',
        'application/rdf+xml',
        'application/rss+xml',
        'application/soap+xml',
        'application/vnd.ogc.se_xml',
        'application/vnd.ogc.wms_xml',
        'application/wsdl+xml',
        'application/xslt+xml',
    ],
    'application/zip': [
        'application/x-shapefile',
        'application/x-tab',
    ],
}

# Media types without an extension or with an extension for which there is already a media type.
valid_media_types = frozenset([item for list in ambiguous_media_types.values() for item in list])



format_corrections = {
    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc4287#section-7
    'atom 1.0': 'application/atom+xml',
    'atom+xml': 'application/atom+xml',
    'xml (atom)': 'application/atom+xml',

    # http://reference.wolfram.com/language/ref/format/DBF.html
    'dbase': 'application/dbf',
    'ms dbase file': 'application/dbf',
    'ms dbase table': 'application/dbf',

    # http://portal.opengeospatial.org/files/?artifact_id=37743
    # http://en.wikipedia.org/wiki/Web_Feature_Service
    # GML is default, but SHP is supported.
    'wfs': 'application/gml+xml',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc7158#section-11
    'applicaton/json': 'application/json',
    'rest json': 'application/json',
    'text/javascript': 'application/json',
    'text/json': 'application/json',
    # http://resources.arcgis.com/en/help/rest/apiref/formattypes.html
    # HTML is default, but JSON and XML are available.
    'arcgis map service': 'application/json',
    'arcgis server': 'application/json',
    'arcgis server rest': 'application/json',
    'esri rest': 'application/json',
    # http://www.odata.org/documentation/odata-version-4-0/
    'odata webservice': 'application/json',

    # http://blogs.msdn.com/b/jaimer/archive/2008/01/04/mime-types.aspx
    'application/accdb': 'application/msaccess',
    'application/vnd.ms-access': 'application/msaccess',
    'msaccess': 'application/msaccess',

    # http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx
    'application/vnd.ms-word': 'application/msword',
    'word': 'application/msword',

    # http://www.w3.org/TR/n-triples/#n-triples-mediatype
    'n-triple': 'application/n-triples',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc2046#section-4.5.1
    'application/octet-string': 'application/octet-stream',
    'application/octet_stream': 'application/octet-stream',
    'application/x-octet-stream': 'application/octet-stream',
    'binary/octet-stream': 'application/octet-stream',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc6713#section-3
    'application/x-gzip': 'application/gzip',
    'gzip': 'application/gzip',
    'tgz': 'application/gzip',
    'txt / gz': 'application/gzip',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc3778
    '0_v2 / pdf': 'application/pdf',
    'aplication/pdf': 'application/pdf',
    'geopdf': 'application/pdf',
    'pdf / pdf': 'application/pdf',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc3870
    'application/xml+rdf': 'application/rdf+xml',
    'image/rdf': 'application/rdf+xml',
    'skos rdf': 'application/rdf+xml',
    'skos webservice': 'application/rdf+xml',
    'text/rdf': 'application/rdf+xml',

    # http://www.rssboard.org/rss-mime-type-application.txt
    'ensearch api': 'application/rss+xml',
    'feed': 'application/rss+xml',
    'rss 1.0': 'application/rss+xml',
    'rss 2.0': 'application/rss+xml',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # https://tools.ietf.org/html/rfc3902
    'soap+xml': 'application/soap+xml',

    # http://www.w3.org/TR/2013/REC-rdf-sparql-XMLres-20130321/#mime
    'api/sparql': 'application/sparql-results+xml',
    'sparql': 'application/sparql-results+xml',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    'kml/google maps': 'application/vnd.google-earth.kml+xml',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    'kml / kmz': 'application/vnd.google-earth.kmz',
    'kml/kmz': 'application/vnd.google-earth.kmz',
    'xml/kml/kmz': 'application/vnd.google-earth.kmz',

    # http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx
    'application/excel': 'application/vnd.ms-excel',
    'application/ms-excel': 'application/vnd.ms-excel',
    'application/msexcel': 'application/vnd.ms-excel',
    'application/vnd.excel': 'application/vnd.ms-excel',
    'application/vnd.msexcel': 'application/vnd.ms-excel',
    'application/x-msexcel': 'application/vnd.ms-excel',
    'application/xls': 'application/vnd.ms-excel',
    'doc_xls': 'application/vnd.ms-excel',
    'excel file': 'application/vnd.ms-excel',
    'excel': 'application/vnd.ms-excel',
    'xls via website': 'application/vnd.ms-excel',
    'xl': 'application/vnd.ms-excel',

    # http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx
    'application/vnd.ms-excel.macroenabled.12': 'application/vnd.ms-excel.sheet.macroEnabled.12',
    'application/xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',

    # http://blogs.msdn.com/b/jaimer/archive/2008/01/04/mime-types.aspx
    'application/vnd.ms-pkistl': 'application/vnd.ms-pki.stl',

    # http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx
    'application/x-mspowerpoint': 'application/vnd.ms-powerpoint',

    # http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx
    'application/docm': 'application/vnd.ms-word.document.macroEnabled.12',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    'application/x-vnd.oasis.opendocument.presentation': 'application/vnd.oasis.opendocument.presentation',

    # http://docs.geoserver.org/stable/en/user/services/wms/reference.html
    'wms': 'application/vnd.ogc.wms_xml',
    'wms_xml': 'application/vnd.ogc.wms_xml',

    # http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx
    'application/pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    # http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx
    'application/vnd.ms-excel.12': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'excel (.xlsx)': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'excel (xlsx)': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'openxml': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    # http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx
    'application/doc': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'ms word': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',

    # http://en.wikipedia.org/wiki/7z
    'lzma': 'application/x-7z-compressed',
    'parco_veicoli_aprile_2014.7z': 'application/x-7z-compressed',
    'parco_veicoli_gennaio_2013.7z': 'application/x-7z-compressed',

    # http://inspire.ec.europa.eu/media-types/
    'arcgis grid format': 'application/x-ascii-grid',
    'arcgrid': 'application/x-ascii-grid',
    'arcinfo grid': 'application/x-ascii-grid',
    'arcinfo workstation grid': 'application/x-ascii-grid',
    'ascii grid': 'application/x-ascii-grid',
    'ascii-grid (arcinfo)': 'application/x-ascii-grid',
    'esri grid': 'application/x-ascii-grid',
    'grid esri': 'application/x-ascii-grid',
    'grid': 'application/x-ascii-grid',
    'raster data set (.grd)': 'application/x-ascii-grid',

    # https://github.com/qgis/QGIS/blob/master/debian/mime/application
    'mif / mid': 'application/x-mapinfo-mif',
    'mif−mid': 'application/x-mapinfo-mif',

    # http://resources.arcgis.com/en/help/main/10.1/index.html#//018s0000000n000000
    'access': 'application/x-msaccess',
    'access.mdb': 'application/x-msaccess',
    'application/mdb': 'application/x-msaccess',
    'arcgis personal geodatabase': 'application/x-msaccess',
    'personal geodatabase feature class': 'application/x-msaccess',
    'personal geodatabase': 'application/x-msaccess',

    # http://en.wikipedia.org/wiki/NetCDF
    'nc(netcdf)': 'application/x-netcdf',
    'netcdf': 'application/x-netcdf',
    'netcdf3': 'application/x-netcdf',

    # http://inspire.ec.europa.eu/media-types/
    'arcgis file geodatabase': 'application/x-filegdb',
    'arcgis geodatabase': 'application/x-filegdb',
    'esri geodatabase feature class': 'application/x-filegdb',
    'fgdb / gdb': 'application/x-filegdb',
    'file geo-database (.gdb)': 'application/x-filegdb',
    'file geodatabase': 'application/x-filegdb',
    'gdb (esri)': 'application/x-filegdb',
    'geodatabase': 'application/x-filegdb',

    # http://en.wikipedia.org/wiki/RAR
    'application/rar': 'application/x-rar-compressed',
    'rar+sas': 'application/x-rar-compressed',

    # http://inspire.ec.europa.eu/media-types/
    'arcgis shapefile': 'application/x-shapefile',
    'esri shape file': 'application/x-shapefile',
    'esri shapefile': 'application/x-shapefile',
    'qgis': 'application/x-shapefile',
    'shape file': 'application/x-shapefile',
    'shape': 'application/x-shapefile',
    'shapefile': 'application/x-shapefile',
    'shapefiler': 'application/x-shapefile',
    'shp': 'application/x-shapefile',
    'shp (cc47)': 'application/x-shapefile',
    'shp (cc48)': 'application/x-shapefile',
    'shp (l93)': 'application/x-shapefile',
    'shp (wgs84)': 'application/x-shapefile',
    'shp / zip': 'application/x-shapefile',
    'tgrshp (compressed)': 'application/x-shapefile',
    'winzipped shapefile': 'application/x-shapefile',
    'zip (shp)': 'application/x-shapefile',
    'zip:shape': 'application/x-shapefile',

    # http://inspire.ec.europa.eu/media-types/
    'tab': 'application/x-tab',

    # http://inspire.ec.europa.eu/media-types/
    'tiff world file': 'application/x-worldfile',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc7303
    # http://tools.ietf.org/html/rfc3023#section-3
    'appication/xml': 'application/xml',
    'application;xml': 'application/xml',
    'text/xml': 'application/xml',
    # http://www.openarchives.org/pmh/
    'oai-pmh (xml repons)': 'application/xml',
    'oai-pmh (xml respons)': 'application/xml',
    'oai-pmh en sru (respons in xml)': 'application/xml',
    'oai-pmh': 'application/xml',
    'xml: oai-pmh dublin core': 'application/xml',
    # http://wiki.openstreetmap.org/wiki/OSM_XML
    'osm': 'application/xml',
    'xml osm': 'application/xml',
    # http://en.wikipedia.org/wiki/Web_Coverage_Service
    # The protocol uses XML, but data is available in multiple formats.
    'wcs': 'application/xml',
    # http://en.wikipedia.org/wiki/XML_Schema_%28W3C%29
    'xsd': 'application/xml',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    'application/x-zip-compressed': 'application/zip',
    'application/zip+text/csv': 'application/zip',
    'csv (inside zip)': 'application/zip',
    'csv (zip)': 'application/zip',
    'csv / zip': 'application/zip',
    'csv file': 'application/zip',
    'csv.zip': 'application/zip',
    'ftp site with zipped esri file geodabases': 'application/zip',
    'uso_suolo_dusaf4_2012_polygon.zip': 'application/zip',
    'zip (csv utf8)': 'application/zip',
    'zip (csv)': 'application/zip',
    'zip (gpx)': 'application/zip',
    'zip (pdf)': 'application/zip',
    'zip (sql + jpeg)': 'application/zip',
    'zip (sql)': 'application/zip',
    'zip / xml': 'application/zip',
    'zip file containing csv files': 'application/zip',
    'zip file containing multiple csv files.': 'application/zip',
    'zip | kml en json': 'application/zip',
    'zip | shape-files + excel': 'application/zip',
    'zip(pdf)': 'application/zip',
    'zip+csv': 'application/zip',
    'zip+pdf': 'application/zip',
    'zip+sas': 'application/zip',
    'zip+sav': 'application/zip',
    'zip+shp': 'application/zip',
    'zip+txt': 'application/zip',
    'zip+xls': 'application/zip',
    'zip+xml': 'application/zip',
    'zip: spss': 'application/zip',
    'zip: xls': 'application/zip',
    'zip:gml': 'application/zip',
    'zip:json': 'application/zip',
    'zip:mdb': 'application/zip',
    'zip:xml en csv': 'application/zip',
    'zip:xml': 'application/zip',
    'zipped esri file geodatabase': 'application/zip',
    # http://www.geobase.ca/geobase/en/data/cded/description.html
    'cdec ascii': 'application/zip',
    # https://developers.google.com/transit/gtfs/reference
    'gtfs': 'application/zip',

    # http://reference.wolfram.com/language/ref/format/BMP.html
    'application/bmp': 'image/bmp',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc2046#section-4.2
    'application/jpg': 'image/jpeg',
    'image/jpg': 'image/jpeg',
    'jpeg (cc48)': 'image/jpeg',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    'jpeg 2000': 'image/jp2',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    'application/tif': 'image/tiff',
    'image/tif': 'image/tiff',
    'multi-page tiff': 'image/tiff',
    'single-page tiff': 'image/tiff',
    'tiff (cc48)': 'image/tiff',
    # http://inspire.ec.europa.eu/media-types/
    'image/geotiff': 'image/tiff',
    'geotif': 'image/tiff',
    'geotiff': 'image/tiff',

    # http://en.wikipedia.org/wiki/MrSID
    'image/x-mrsid-image': 'image/x-mrsid-image',
    'mrsid': 'image/x-mrsid-image',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc5545#section-8.1
    'icalendar': 'text/calendar',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc4180#section-3
    'application/csv': 'text/csv',
    'application/cvs': 'text/csv',
    'aug 2014 / csv': 'text/csv',
    'csv"': 'text/csv',
    'csv(txt)': 'text/csv',
    'csv-semicolon delimited': 'text/csv',
    'csv-tab delimited': 'text/csv',
    'csv/api': 'text/csv',
    'csv/txt': 'text/csv',
    'csv/utf8': 'text/csv',
    'csv/webservice/api': 'text/csv',
    'jul 2014 / csv': 'text/csv',
    'link_csv': 'text/csv',
    'text (csv)': 'text/csv',
    'text(csv)': 'text/csv',
    'text/comma-separated-values': 'text/csv',
    'text/cvs': 'text/csv',
    'text/x-comma-separated-values': 'text/csv',
    'text;csv': 'text/csv',
    'txt/cvs': 'text/csv',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    'application/htm': 'text/html',
    'application/html': 'text/html',
    'arcgis map preview': 'text/html',
    'arcgis online map': 'text/html',
    'hmtl': 'text/html',
    'home page': 'text/html',
    'html+rdfa': 'text/html',
    'html5': 'text/html',
    'link': 'text/html',
    'link_html': 'text/html',
    'map portal': 'text/html',
    'portal': 'text/html',
    'query tool': 'text/html',
    'search, view & download data': 'text/html',
    'sparql web form': 'text/html',
    'texl/html': 'text/html',
    'text/htm': 'text/html',
    'web': 'text/html',
    'web browser display': 'text/html',
    'web page': 'text/html',
    'web site': 'text/html',
    'web tool': 'text/html',
    'web-interface': 'text/html',
    'webinterface': 'text/html',
    'webpage': 'text/html',
    'website': 'text/html',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://tools.ietf.org/html/rfc2046#section-4.1.3
    'ascii': 'text/plain',
    'dat': 'text/plain',
    'fixed-length ascii text': 'text/plain',
    'plain': 'text/plain',
    'text/txt': 'text/plain',
    'texte': 'text/plain',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    'application/rtf': 'text/rtf',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    'text/tab': 'text/tab-separated-values',

    # http://www.iana.org/assignments/media-types/media-types.xhtml
    # http://www.w3.org/TeamSubmission/turtle/#sec-mime
    'rdf/turtle': 'text/turtle',
    'turtle': 'text/turtle',

    # http://en.wikipedia.org/wiki/Flash_Video
    'flash': 'video/x-flv',
}

# Media types that are as good as nil.
ignore_media_types = frozenset([
    '""',
    'all',
    'api',
    'application/octet-stream',
    'application/unknown',
    'application/x-unknown-content-type',
    'cd-rom',
    'data file',
    'geospatial',
    'image',
    'img',
    'map',
    'meta/void',
    'n/a',
    'no-type',
    'rest',
    'service',
    'tool',
    'unknown/unknown',
    'upon request',
    'url',
    'variable',
    'varies',
    'varies upon user output',
    'various',
    'various formats',
    'viewservice',
    'webservice',
    'widget',
    'wmf & wfs',
    'wms & wfs',

    # Download
    'application/force-download',
    'application/save',
    'application/x-download',
    'force-download',

    # Error
    '15 kb',

    # Multiple (semi-colon)
    'csv/txt; pdf',
    'csv/txt; sgml; xml',
    'csv/txt; sgml; xml',
    'csv/txt; xml; tiff',
    'sgml; xml; tiff',
    'web service (xml); web service (ansi z39.50), images, documents',
    'xml; tiff',
    'xml; tiff',
    # Multiple (slash)
    'pdf/webpages',
    'xml/tiff/jpeg',
    'xml/tiff/jpg',
    # Multiple (conjunction)
    'api: xml en jpeg',
    'xls en csv',

    # Other
    'altro', # IT
    'autre', # FR
    'other', # EN

    # Programming language
    'ashx',  # ASP.NET
    'asp',  # Active Server Pages
    'aspx',  # ASP.NET
    'axd',  # ASP.NET
    'do',  # Java Struts
    'jsp',  # JavaServer Pages
    'php',  # PHP
    'shtml',  # Server Side Includes

    # Software
    'mobile application',
    'cross-platform java-based desktop software',

    # No standard media type
    # @see http://en.wikipedia.org/wiki/Shapefile
    'sbn',
    'sbx',
])
