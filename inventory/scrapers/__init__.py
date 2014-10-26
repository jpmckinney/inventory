from .base import Catalog
from .ckan import CKAN

catalogs = [
    Catalog('ar', 'http://datospublicos.gob.ar/data/', scraper=CKAN),
    Catalog('au', 'http://data.gov.au/', scraper=CKAN),
    Catalog('br', 'http://dados.gov.br/', scraper=CKAN),
    Catalog('ca', 'http://data.gc.ca/data/en/', scraper=CKAN),
    Catalog('gb', 'http://data.gov.uk/', scraper=CKAN, parameters={'fq': 'license_id-is-ogl:true'}),
    Catalog('id', 'http://data.id/', scraper=CKAN),
    Catalog('ie', 'http://data.gov.ie/', scraper=CKAN),
    Catalog('it', 'http://www.dati.gov.it/catalog/', scraper=CKAN),
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

    # CKAN is hidden:
    # http://data.gouv.fr/
    # http://data.norge.no/

    # Catalog('cl', 'http://datos.gob.cl/', scraper=Junar),
    # Catalog('cr', 'http://datosabiertos.gob.go.cr/', scraper=Junar),
    # Catalog('mk', 'http://opendata.gov.mk/', scraper=OGDI),
    # Catalog('co', 'http://datos.gov.co/', scraper=OGDI),
    # Catalog('gr', 'http://data.gov.gr/', scraper=OpenColibri),
    # Catalog('ke', 'http://opendata.go.ke/', scraper=Socrata),

    # Catalog('dk', 'http://data.digitaliser.dk/'),  # 757
    # Catalog('es', 'http://datos.gob.es/'),  # 2572
    # Catalog('fi', 'http://data.suomi.fi/'),  # <50
    # Catalog('ge', 'http://data.gov.ge/'),
    # Catalog('gh', 'http://data.gov.gh/'),  # 1068
    # Catalog('il', 'http://data.gov.il/'),
    # Catalog('jo', 'http://www.jordan.gov.jo/wps/portal/OpenData_en'),  # <100
    # Catalog('kr', 'https://www.data.go.kr/'),  # 9268
    # Catalog('lt', 'http://opendata.gov.lt/'),  # 262
    # Catalog('mt', 'http://data.gov.mt/'),  # 4
    # Catalog('nz', 'http://data.govt.nz/'),  # 2559
    # Catalog('tn', 'http://data.gov.tn/'),  # 133
    # Catalog('ua', 'http://data.gov.ua/'),  # 100
]
