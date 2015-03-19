import json
import sys
from collections import defaultdict
from optparse import make_option
from urllib.parse import urlparse

import ckanapi
import pandas as pd
import lxml
from django.db.models import Count

from . import InventoryCommand
from inventory.models import Dataset, Distribution
from inventory.scrapers import CKAN


class Command(InventoryCommand):
    help = 'Analyzes catalogs'

    option_list = InventoryCommand.option_list + (
        make_option('--access', action='append_const', dest='reports', const='access',
                    help='Classification of direct download domain names, for import into R.'),
        make_option('--api', action='append_const', dest='reports', const='api',
                    help='Usage of catalog API technologies.'),
        make_option('--dcat', action='append_const', dest='reports', const='dcat',
                    help='Usage of DCAT by CKAN catalogs.'),
        make_option('--pod', action='append_const', dest='reports', const='pod',
                    help='Usage of Project Open Data Metadata Schema.'),
        make_option('--schemaorg', action='append_const', dest='reports', const='schemaorg',
                    help='Usage of Schema.org.'),
        make_option('--federation', action='append_const', dest='reports', const='federation',
                    help='Usage of Federation technologies.'),
        make_option('--licenses', action='append_const', dest='reports', const='licenses',
                    help='Usage of licenses.'),
        make_option('--csv', action='store_const', dest='format', const='csv',
                    default='table',
                    help='Prints the results as CSV.'),
    )

    def handle(self, *args, **options):
        self.setup(*args, **options)

        for report in options['reports']:
            result = getattr(self, report)()
            if result is not None:
                if options['format'] == 'table':
                    result.to_string(sys.stdout)
                elif options['format'] == 'csv':
                    result.to_csv(sys.stdout)

    def series(self, getter):
        series = {}
        for catalog in self.catalogs:
            series[catalog.division_id] = getter(catalog)
        return pd.Series(series)

    def api(self):
        def getter(catalog):
            if issubclass(catalog.scraper, CKAN):
                try:
                    client = ckanapi.RemoteCKAN(catalog.url, get_only=catalog.get_only)
                    status_show = client.call_action('status_show', verify=catalog.verify)
                    return int('datastore' in status_show['extensions'])
                except ckanapi.errors.CKANAPIError:
                    pass

        return self.series(getter)

    def dcat(self):
        def getter(catalog):
            if issubclass(catalog.scraper, CKAN):
                datasets = Dataset.objects.filter(division_id=catalog.division_id)
                if datasets.exists():
                    response = self.get(catalog.dataset_url(datasets[0]))
                    if response.status_code == 200:
                        response = self.get(catalog.dataset_rdf_url(datasets[0]))
                        return int(response.status_code == 200)

        return self.series(getter)

    def pod(self):
        def getter(catalog):
            response = self.get(catalog.data_json_url)
            return int(response.status_code == 200)

        return self.series(getter)

    def schemaorg(self):
        def getter(catalog):
            datasets = Dataset.objects.filter(division_id=catalog.division_id)
            if datasets.exists():
                url = catalog.dataset_url(datasets[0])
                if url:
                    response = self.get(url)
                    if response.status_code == 200:
                        return int('http://schema.org/Dataset' in response.text)

        return self.series(getter)

    def access(self):
        frame = defaultdict(lambda: defaultdict(int))
        for catalog in self.catalogs:
            urls = Distribution.objects.filter(division_id=catalog.division_id).values_list('accessURL', flat=True)
            if urls:
                frame['count'][catalog.division_id] = urls.count()
                for url in urls:
                    host = urlparse(url).netloc.split(':', 1)[0]
                    if host.endswith(catalog_domains[catalog.division_id]):
                        key = 'Catalog'
                    elif any(host.endswith(suffix) for suffix in government_domains[catalog.division_id]):
                        key = 'Government'
                    else:
                        key = 'Other'
                        # frame[host][catalog.division_id] += 1
                    frame[key][catalog.division_id] += 1
        return pd.DataFrame(frame)

    def federation(self):
        frame = defaultdict(lambda: defaultdict(int))
        for catalog in self.catalogs:
            # Assumes we don't need to paginate.
            if issubclass(catalog.scraper, CKAN):
                client = ckanapi.RemoteCKAN(catalog.url, get_only=catalog.get_only)
                package_search = client.call_action('package_search', {'fq': 'type:harvest', 'rows': 300000}, verify=catalog.verify)

                if package_search['results']:
                    for package in package_search['results']:
                        source_type = self.source_type(catalog, package)
                        if source_type:
                            frame[source_type][catalog.division_id] += 1
                        else:
                            self.warning('could not determine source type of {}'.format(catalog.dataset_api_url(package)))
                # GB
                else:
                    try:
                        for package in client.call_action('harvest_source_list', verify=catalog.verify):
                            if package['active']:
                                source_type = normalize_source_type(package, package['type'])
                                if source_type:
                                    frame[source_type][catalog.division_id] += 1
                                else:
                                    self.warning('could not determine source type of {}'.format(catalog.harvest_api_url(package)))
                    except ckanapi.errors.CKANAPIError:
                        pass
            elif catalog.scraper.__name__ == 'Socrata':
                if 'federation_filter' in self.get(catalog.url).text:
                    frame['socrata'][catalog.division_id] = 1
        return pd.DataFrame(frame)

    def licenses(self):
        frame = defaultdict(lambda: defaultdict(int))
        for catalog in self.catalogs:
            for value in Dataset.objects.filter(division_id=catalog.division_id).values('license').annotate(count=Count('id', distinct=True)).order_by('count').iterator():
                frame[catalog.division_id][value['license']] = value['count']
        return pd.DataFrame(frame)

    def report(self, klass, field, *, distinct):
        for catalog in self.catalogs:
            count = Dataset.objects.filter(division_id=catalog.division_id).count()
            print('{} ({})'.format(catalog.division_id, count))
            for value in klass.objects.filter(division_id=catalog.division_id).values(field).annotate(count=Count(distinct, distinct=True)).order_by('count').iterator():
                print('  {:7.2%} {} ({})'.format(value['count'] / count, value[field], value['count']))

    def source_type(self, catalog, package):
        # AU, FI, IE, IT, MX, PY
        if package.get('source_type'):
            return normalize_source_type(package, package['source_type'])

        # IT
        elif '/api/rest/dataset/' in package['url']:
            url, name = package['url'].split('api/rest/dataset/', 1)
            return self.source_type(catalog, ckanapi.RemoteCKAN(url).call_action('package_show', {'id': name}))

        # US
        # @see https://github.com/ckan/ckanext-spatial/blob/master/doc/harvesters.rst
        # @see https://github.com/GSA/ckanext-geodatagov/tree/master/ckanext/geodatagov/harvesters
        elif package.get('extras'):
            source_type = next(extra['value'] for extra in package['extras'] if extra['key'] == 'source_type')
            # @see https://github.com/GSA/ckanext-geodatagov/blob/master/ckanext/geodatagov/harvesters/base.py#L174
            if source_type == 'single-doc':
                response = self.get(package['url'])
                if response.status_code == 200:
                    try:
                        return normalize_metadata_scheme(response)
                    except lxml.etree.XMLSyntaxError:
                        pass
            # @see https://github.com/GSA/ckanext-geodatagov/blob/master/ckanext/geodatagov/harvesters/waf_collection.py
            elif source_type == 'waf-collection':
                # @see https://github.com/GSA/ckanext-geodatagov/blob/master/ckanext/geodatagov/validation/__init__.py
                config = json.loads(next(extra['value'] for extra in package['extras'] if extra['key'] == 'config'))
                if config.get('validator_profiles'):
                    if len(config['validator_profiles']) > 1:
                        self.warning('multiple validator_profiles for {}'.format(catalog.dataset_api_url(package)))
                    else:
                        return 'waf-{}'.format(validators[config['validator_profiles'][0]])
                else:
                    response = self.get(config['collection_metadata_url'])
                    if response.status_code == 200:
                        scheme = normalize_metadata_scheme(response)
                        if scheme:
                            return 'waf-{}'.format(scheme)
            else:
                normalized = normalize_source_type(package, source_type)
                if normalized:
                    return normalized

        # BR
        else:
            try:
                if ckanapi.RemoteCKAN(package['url']).call_action('site_read'):
                    return 'ckan'
            except ckanapi.errors.CKANAPIError:
                pass


def normalize_source_type(package, source_type):
    if source_type in source_types:
        return source_types[source_type]
    elif package['url'].endswith('/csw') or '/csw/' in package['url']:
        return 'csw'


def normalize_metadata_scheme(response):
    if 'FGDC-STD-001-1998' in response.text:
        return 'fgdc'
    elif lxml.etree.fromstring(response.content).xpath('/MD_Metadata|/gmi:MI_Metadata', namespaces={'gmi': 'http://www.isotc211.org/2005/gmi'}):
        return 'iso19139'


source_types = {
    # Dynamic API
    'arcgis': 'arcgis',
    'ckan': 'ckan',
    'csw': 'csw',
    'waf': 'waf',
    # GB
    'gemini-waf': 'waf-gemini',
    # US
    # @see https://github.com/GSA/ckanext-geodatagov/blob/master/ckanext/geodatagov/harvesters/base.py#L185
    'geoportal': 'csw',
    # @see https://github.com/GSA/ckanext-geodatagov/blob/master/ckanext/geodatagov/harvesters/z3950.py
    'z3950': 'iso23950',

    # Static file
    # GB
    'dcat_rdf': 'dcat_rdf',
    'data_json': 'dcat_json',
    'gemini-single': 'gemini',
    'inventory': 'datashare',
    # MX
    'dcat_json': 'pod',  # v1.0
    # US
    'datajson': 'pod',
}

validators = {
    'fgdc_minimal': 'fgdc',
    'iso19139ngdc': 'iso19139',
}

catalog_domains = {
    'ocd-division/country:ar': 'datospublicos.gob.ar',
    'ocd-division/country:au': 'data.gov.au',
    'ocd-division/country:br': 'dados.gov.br',
    'ocd-division/country:ca': 'data.gc.ca',
    'ocd-division/country:cl': 'datos.gob.cl',
    'ocd-division/country:cr': 'gobiernodigitalcr.cloudapi.junar.com',
    'ocd-division/country:ee': 'opendata.riik.ee',
    'ocd-division/country:es': 'datos.gob.es',
    'ocd-division/country:fi': 'avoindata.fi',
    'ocd-division/country:fr': 'data.gouv.fr',
    'ocd-division/country:gb': 'data.gov.uk',
    'ocd-division/country:gh': 'data.gov.gh',
    'ocd-division/country:gr': 'data.gov.gr',
    'ocd-division/country:id': 'data.id',
    'ocd-division/country:ie': 'data.gov.ie',
    'ocd-division/country:it': 'dati.gov.it',
    'ocd-division/country:ke': 'opendata.go.ke',
    'ocd-division/country:md': 'data.gov.md',
    'ocd-division/country:mx': 'datos.gob.mx',
    'ocd-division/country:nl': 'data.overheid.nl',
    'ocd-division/country:ph': 'data.gov.ph',
    'ocd-division/country:py': 'datos.gov.py',
    'ocd-division/country:ro': 'data.gov.ro',
    'ocd-division/country:se': 'oppnadata.se',
    'ocd-division/country:sk': 'data.gov.sk',
    'ocd-division/country:tz': 'opendata.go.tz',
    'ocd-division/country:us': 'data.gov',
    'ocd-division/country:uy': 'catalogodatos.gub.uy',
}

# We only categorize the most popular domains, i.e. >=0.1% of distributions.
government_domains = {
    'ocd-division/country:ar': ['.gob.ar'],
    'ocd-division/country:au': ['.gov.au'],
    'ocd-division/country:br': [
        '.gov.br',
        '.jus.br',
        '.leg.br',
    ],
    'ocd-division/country:ca': [
        '.gc.ca',
        'geobase.ca',  # Natural Resources Canada
    ],
    'ocd-division/country:cl': ['.gob.cl'],
    'ocd-division/country:cr': ['.go.cr'],
    'ocd-division/country:ee': [
        '.riik.ee',  # "state"
        '.muinas.ee',  # http://et.wikipedia.org/wiki/Muinsuskaitseamet
    ],
    'ocd-division/country:es': [
        '.gob.es',
        '.cnig.es',  # Centro Nacional de Información Geográfica
        '.chj.es',  #  Confederación Hidrográfica del Júcar
        '.agenciatributaria.es',  # Agencia Tributaria
        '.fega.es',  # Fondo Español de Garantía Agraria
        '.ign.es',  #  Instituto Geográfico Nacional
        '.imserso.es',  # Instituto de Mayores y Servicios Sociales
        '.ine.es',  # Instituto Nacional de Estadística
        '.ipyme.org',  # Dirección General de Industria y de la Pequeña y Mediana Empresa
        '.cis.es',  # Centro de investigaciones sociológicas
    ],
    'ocd-division/country:fi': [  # 0.005
        '.gtk.fi',  # Geological Survey of Finland
        '.liikennevirasto.fi',  # Finnish Transport Agency
        '.maanmittauslaitos.fi',  # National Land Survey
        '.paikkatietoikkuna.fi',  # National Land Survey
        '.sfs.fi',  # Finnish Standards Association
        '.stat.fi',  # Statistics Finland
        '.vahtiohje.fi',  # Ministry of Finance
    ],
    'ocd-division/country:fr': ['.gouv.fr'],
    'ocd-division/country:gb': [
        '.gov.uk',
        '.hpa.org.uk',  # Public Health England
        '.isdscotland.org',  # Scottish Government
        '.nhs.uk',  # Department of Health
        '.ordnancesurvey.co.uk',  # Department for Business, Innovation and Skills
        '.slc.co.uk',  # http://en.wikipedia.org/wiki/Student_Loans_Company
        '.uktradeinfo.com',  # HM Revenue and Customs
        'opendatacommunities.org',  # Department for Communities and Local Government
    ],
    'ocd-division/country:gh': ['.gov.gh'],
    'ocd-division/country:gr': [  # 0.005
        '.gov.gr',
        '.astynomia.gr',  # http://en.wikipedia.org/wiki/Hellenic_Police
        '.ekdd.gr',  # http://en.wikipedia.org/wiki/National_Centre_for_Public_Administration_and_Local_Government
    ],
    'ocd-division/country:id': ['.go.id'],
    'ocd-division/country:ie': [  # 0.005
        '.gov.ie',
        '.marine.ie',  # Marine Institute
        '.cso.ie',  # Central Statistics Office Ireland
        '.hea.ie',  # Higher Education Authority
        '.buildingsofireland.ie',  # Department of Arts, Heritage and the Gaeltacht
        '.epa.ie',  # Environmental Protection Agency
        '.education.ie',  # Department of Education and Skills
        '.environ.ie',  # Department of the Environment, Community and Local Government
        '.fishingnet.ie',  # Department of Agriculture, Food and the Marine
        '.gsi.ie',  # Geological Survey of Ireland
        '.infomar.ie',  # Geological Survey of Ireland / Marine Institute
        '.seai.ie',  # Sustainable Energy Authority
    ],
    'ocd-division/country:it': [
        '.gov.it',
        '.inail.it',  # Istituto Nazionale Assicurazione contro gli Infortuni sul Lavoro
        '.inps.it',  # Istituto Nazionale Previdenza Sociale
        '.istat.it',  # Istituto nazionale di statistica
        '.politicheagricole.it',  # Ministero delle politiche agricole alimentari e forestali
    ],
    'ocd-division/country:ke': [
        '.go.ke',
        '.kenyalaw.org',  # National Council for Law Reporting
    ],
    'ocd-division/country:md': [
        '.gov.md',
        '.statistica.md',  # Biroul Naţional de Statistică al Republicii Moldova
        '.knbs.or.ke',  # Kenya National Bureau of Statistics
    ],
    'ocd-division/country:mx': [
        '.gob.mx',
        '.nafin.com',  # Nacional Financiera, state bank
        '.pemex.com',  # Petróleos Mexicanos, state-owned
    ],
    'ocd-division/country:nl': [
        '.duo.nl',  # Ministerie van Onderwijs, Cultuur en Wetenschap
        '.gdngeoservices.nl',  # Geologische Dienst Nederland
        '.kaartenbalie.nl',  # Ministerie van Economische Zaken
        '.kadaster.nl',  # Cadastre, Land Registry and Mapping Agency
        '.knmi.nl',  # Ministry of Infrastructure and the Environment
        '.nationaalgeoregister.nl',
        '.overheid.nl', # "government"
        '.pbl.nl',  # Planbureau voor de Leefomgeving
        '.rijkswaterstaat.nl',  # Ministerie van Infrastructuur en Milieu
        '.risicokaart.nl',
        '.rivm.nl',  # Ministerie van Volksgezondheid, Welzijn en Sport
        '.rwsgeoweb.nl',
        '.waterschapservices.nl',
    ],
    'ocd-division/country:ph': ['.gov.ph'],
    'ocd-division/country:py': ['.gov.py'],
    'ocd-division/country:ro': [  # 0.005
        '.gov.ro',
        '.edu.ro',  # Ministerul Educației Naționale
        '.inforegio.ro',  # Ministry of Regional Development and Public Administration
        '.mfinante.ro',  # Ministerul Finanţelor Publice
        '.mmuncii.ro',  # Ministerul Muncii, Familiei, Protecţiei Sociale şi Persoanelor Vârstnice
    ],
    'ocd-division/country:se': [  # 0.025
        '.gov.se',
        '.sgu.se',  # http://en.wikipedia.org/wiki/Geological_Survey_of_Sweden
        '.socialstyrelsen.se',  # http://en.wikipedia.org/wiki/National_Board_of_Health_and_Welfare_%28Sweden%29
        '.verksamt.se',
    ],
    'ocd-division/country:sk': [  # 0.005
        '.gov.sk',
        '.justice.sk',  # Ministerstvo Spravodlivosti
        '.mfa.sk',  # Ministry of Foreign and European Affairs of the Slovak Republic
        '.mhsr.sk',  # Ministry of Economy of the Slovak Republic
        '.minv.sk',  # Ministry of Interior of the Slovak Republic
        '.mosr.sk',  # Ministry of Defense of Slovak Republic
        '.mpsr.sk',  # Ministry of Agriculture and Rural Development of the Slovak Republic
        '.nrsr.sk',  # National Council of the Slovak Republic
        '.sazp.sk',  #  Slovenská agentúra životného prostredia
        '.skgeodesy.sk',  # Geodesy, Cartography and Cadastre Authority of Slovak Republic
        '.statistics.sk',  # Statistical Office of the Slovak Republic
        '.svssr.sk',  # State Veterinary and Food Administration of the Slovak Republic
    ],
    'ocd-division/country:tz': ['.go.tz'],
    'ocd-division/country:us': [
        '.gov',
        '.mil',
    ],
    'ocd-division/country:uy': [
        '.gub.uy',
        '.precios.uy',  #  Ministerio de Economía y Finanzas
    ],
}
