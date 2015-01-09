from .base import Catalog
from .ckan import CKAN
from .open_colibri import OpenColibri
from .junar import Junar
from .socrata import Socrata

catalogs = [
    Catalog('ar', 'http://datospublicos.gob.ar/data/', scraper=CKAN),
    Catalog('au', 'http://data.gov.au/', scraper=CKAN),
    Catalog('br', 'http://dados.gov.br/', scraper=CKAN),
    Catalog('ca', 'http://data.gc.ca/data/en/', scraper=CKAN),
    Catalog('cl', 'http://api.recursos.datos.gob.cl/', scraper=Junar, parameters={'auth_key': '6ae305b9ad9923f768879e851addf143c3461182'}),
    Catalog('cr', 'http://gobiernodigitalcr.cloudapi.junar.com/', scraper=Junar, parameters={'auth_key': 'a99bb53e81c5fcaec72fd313fcb97c7306e13d3d'}),
    Catalog('gb', 'http://data.gov.uk/', scraper=CKAN, parameters={'fq': 'license_id-is-ogl:true'}),
    Catalog('gr', 'http://data.gov.gr/', scraper=OpenColibri),
    Catalog('id', 'http://data.id/', scraper=CKAN),
    Catalog('ie', 'http://data.gov.ie/', scraper=CKAN),
    Catalog('it', 'http://www.dati.gov.it/catalog/', scraper=CKAN),
    Catalog('ke', 'https://opendata.go.ke/', scraper=Socrata),
    Catalog('md', 'http://data.gov.md/ckan', scraper=CKAN),
    Catalog('mx', 'http://catalogo.datos.gob.mx/', scraper=CKAN),
    Catalog('nl', 'https://data.overheid.nl/data/', scraper=CKAN, get_only=False),
    Catalog('ph', 'http://data.gov.ph/catalogue/', scraper=CKAN),
    Catalog('py', 'http://datos.gov.py/', scraper=CKAN),
    Catalog('ro', 'http://data.gov.ro/', scraper=CKAN),
    Catalog('se', 'http://oppnadata.se/', scraper=CKAN),
    Catalog('sk', 'http://data.gov.sk/', scraper=CKAN),
    Catalog('tz', 'http://opendata.go.tz/', scraper=CKAN),
    Catalog('us', 'http://catalog.data.gov/', scraper=CKAN),
    Catalog('uy', 'https://catalogodatos.gub.uy/', scraper=CKAN),


    # Canadian cities
    Catalog('mtl', 'http://donnees.ville.montreal.qc.ca/', scraper=CKAN),
    Catalog('shr', 'http://donnees.ville.sherbrooke.qc.ca/', scraper=CKAN),
    Catalog('ott', 'http://data.ottawa.ca/', scraper=CKAN),
    Catalog('sur', 'http://data.surrey.ca/', scraper=CKAN),
    Catalog('wrc', 'http://data.whiterockcity.ca/', scraper=CKAN),
    Catalog('tol', 'https://data.tol.ca/', scraper=Socrata),
    Catalog('edm', 'https://data.edmonton.ca/', scraper=Socrata),
    Catalog('peg', 'https://data.winnipeg.ca/', scraper=Socrata),
    Catalog('stc', 'https://data.strathcona.ca/', scraper=Socrata),     
    # Over 1000:
    # Catalog('fr', 'http://data.gouv.fr/'), # 13756 CKAN is hidden API https://www.data.gouv.fr/fr/apidoc/
    # Catalog('kr', 'https://www.data.go.kr/'),  # 9268 API
    # Catalog('es', 'http://datos.gob.es/'),  # 2572 Drupal http://datos.gob.es/sites/default/files/catalogo.rdf
    # Catalog('nz', 'http://data.govt.nz/'),  # 2559 SilverStripe RSS
    # Catalog('gh', 'http://data.gov.gh/'),  # 1068 OGPL http://data.gov.gh/dataset-rss.xml

    # Over 100:
    # Catalog('co', 'http://datos.gov.co/', scraper=OGDI),  # 672
    # Catalog('mk', 'http://opendata.gov.mk/', scraper=OGDI),  # 154
    # Catalog('dk', 'http://data.digitaliser.dk/'),  # 757
    # Catalog('no', 'http://data.norge.no/'), # 420 CKAN is hidden Drupal http://data.norge.no/taxonomy/term/###/all/feed?page=#
    # Catalog('lt', 'http://opendata.gov.lt/'),  # 262
    # Catalog('il', 'http://data.gov.il/'),  # 243 Drupal
    # Catalog('tn', 'http://data.gov.tn/'),  # 133 Joomla! pagination, tabular
    # Catalog('ua', 'http://data.gov.ua/'),  # 100 Drupal RDFa, /api/action/package_list returns the dcterms:identifier of datasets

    # Under 100:
    # Catalog('jo', 'http://www.jordan.gov.jo/wps/portal/OpenData_en'),  # <100
    # Catalog('fi', 'http://data.suomi.fi/'),  # <50
    # Catalog('ge', 'http://data.gov.ge/'),  # 14
    # Catalog('mt', 'http://data.gov.mt/'),  # 4
]
