from .base import Catalog

from .ckan import CKAN
from .junar import Junar
from .open_colibri import OpenColibri
from .socrata import Socrata

from .rdf import RDF
from .rss import RSS

from .fr import Fr

catalogs = [
    Catalog('ocd-division/country:ar', 'http://datospublicos.gob.ar/data/', scraper=CKAN),
    Catalog('ocd-division/country:au', 'http://data.gov.au/', scraper=CKAN),
    Catalog('ocd-division/country:br', 'http://dados.gov.br/', scraper=CKAN),
    Catalog('ocd-division/country:ca', 'http://data.gc.ca/data/en/', scraper=CKAN),
    Catalog('ocd-division/country:cl', 'http://api.recursos.datos.gob.cl/', scraper=Junar, parameters={'auth_key': '6ae305b9ad9923f768879e851addf143c3461182'}),
    Catalog('ocd-division/country:cr', 'http://gobiernodigitalcr.cloudapi.junar.com/', scraper=Junar, parameters={'auth_key': 'a99bb53e81c5fcaec72fd313fcb97c7306e13d3d'}),
    Catalog('ocd-division/country:ee', 'https://opendata.riik.ee/', scraper=CKAN, get_only=False),
    Catalog('ocd-division/country:es', 'http://datos.gob.es/sites/default/files/catalogo.rdf', scraper=RDF),
    Catalog('ocd-division/country:fi', 'https://www.avoindata.fi/data/en/', scraper=CKAN),
    Catalog('ocd-division/country:fr', 'https://www.data.gouv.fr/', scraper=Fr),
    Catalog('ocd-division/country:gb', 'http://data.gov.uk/', scraper=CKAN, parameters={'fq': 'license_id-is-ogl:true'}),
    Catalog('ocd-division/country:gh', 'http://data.gov.gh/dataset-rss.xml', scraper=RSS),  # OGPL
    Catalog('ocd-division/country:gr', 'http://data.gov.gr/', scraper=OpenColibri),
    Catalog('ocd-division/country:id', 'http://data.id/', scraper=CKAN),
    Catalog('ocd-division/country:ie', 'http://data.gov.ie/', scraper=CKAN),
    Catalog('ocd-division/country:it', 'http://www.dati.gov.it/catalog/', scraper=CKAN),
    Catalog('ocd-division/country:ke', 'https://opendata.go.ke/', scraper=Socrata),
    Catalog('ocd-division/country:md', 'http://data.gov.md/ckan', scraper=CKAN),
    Catalog('ocd-division/country:mx', 'http://catalogo.datos.gob.mx/', scraper=CKAN),
    Catalog('ocd-division/country:nl', 'https://data.overheid.nl/data/', scraper=CKAN, get_only=False),
    Catalog('ocd-division/country:ph', 'http://data.gov.ph/catalogue/', scraper=CKAN),
    Catalog('ocd-division/country:py', 'http://datos.gov.py/', scraper=CKAN),
    Catalog('ocd-division/country:ro', 'http://data.gov.ro/', scraper=CKAN),
    Catalog('ocd-division/country:se', 'http://oppnadata.se/', scraper=CKAN),
    Catalog('ocd-division/country:sk', 'http://data.gov.sk/', scraper=CKAN),
    Catalog('ocd-division/country:tz', 'http://opendata.go.tz/', scraper=CKAN),
    Catalog('ocd-division/country:us', 'http://catalog.data.gov/', scraper=CKAN, parameters={'fq': 'organization_type:"Federal Government"'}),
    Catalog('ocd-division/country:uy', 'https://catalogodatos.gub.uy/', scraper=CKAN),

    # Canadian municipalities # @todo Use census subdivision codes, omit by default
    Catalog('ocd-division/country:ca/csd:2466023', 'http://donnees.ville.montreal.qc.ca/', scraper=CKAN),
    Catalog('ocd-division/country:ca/csd:2443027', 'http://donnees.ville.sherbrooke.qc.ca/', scraper=CKAN),
    Catalog('ocd-division/country:ca/csd:3506008', 'http://data.ottawa.ca/', scraper=CKAN),
    Catalog('ocd-division/country:ca/csd:5915004', 'http://data.surrey.ca/', scraper=CKAN),
    Catalog('ocd-division/country:ca/csd:5915007', 'http://data.whiterockcity.ca/', scraper=CKAN),
    Catalog('ocd-division/country:ca/csd:5915001', 'https://data.tol.ca/', scraper=Socrata),
    Catalog('ocd-division/country:ca/csd:4811061', 'https://data.edmonton.ca/', scraper=Socrata),
    Catalog('ocd-division/country:ca/csd:4611040', 'https://data.winnipeg.ca/', scraper=Socrata),
    Catalog('ocd-division/country:ca/csd:4811052', 'https://data.strathcona.ca/', scraper=Socrata),


    # Over 1000:
    # Catalog('ocd-division/country:kr', 'https://www.data.go.kr/'),  # 9268 need a Korean translator for API documentation
    # Catalog('ocd-division/country:nz', 'http://data.govt.nz/'),  # 2559 SilverStripe, RSS but no pagination

    # Over 100:
    # Catalog('ocd-division/country:dk', 'http://data.digitaliser.dk/'),  # 757
    # Catalog('ocd-division/country:no', 'http://data.norge.no/'), # 420 Drupal CKAN is hidden
    #   Each category has an XML link in <head>. Datasets repeat across categories.
    #   <link rel="alternate" type="application/rss+xml" title="xxx" href="http://data.norge.no/taxonomy/term/###/all/feed?type=3" />
    # Catalog('ocd-division/country:lt', 'http://opendata.gov.lt/'),  # 262
    # Catalog('ocd-division/country:il', 'http://data.gov.il/'),  # 243 Drupal
    # Catalog('ocd-division/country:tn', 'http://data.gov.tn/'),  # 133 Joomla!
    # Catalog('ocd-division/country:ua', 'http://data.gov.ua/'),  # 100 Drupal, RDFa
    #   /api/action/package_list returns the dcterms:identifier of datasets, but
    #   no discoverable API accepts an identifier as a parameter

    # Under 100:
    # Catalog('ocd-division/country:jo', 'http://www.jordan.gov.jo/wps/portal/OpenData_en'),  # <100
    # Catalog('ocd-division/country:ge', 'http://data.gov.ge/'),  # 14
    # Catalog('ocd-division/country:mt', 'http://data.gov.mt/'),  # 4

    # OGDI's API publishes data, not metadata.
    # Catalog('ocd-division/country:co', 'http://datos.gov.co/', scraper=OGDI),  # 672
    #   404 curl http://servicedatosabiertoscolombia.cloudapp.net/DataCatalog/DataSets --data 'pageSize=1000&pageNumber=1'
    #   404 curl http://datosabiertoscolombia.cloudapp.net/DataCatalog/DataSets --data 'pageSize=1000&pageNumber=1'
    # Catalog('ocd-division/country:mk', 'http://opendata.gov.mk/', scraper=OGDI),  # 154
    #   200 curl http://ogdi.otvorenipodatoci.gov.mk/DataCatalog/DataSets --data 'pageSize=1000&pageNumber=1'
    #   200 curl http://ogdiotvorenipodatocigovmk.cloudapp.net:8080/v1/OtvoreniPodatoci/AEKNotificiraniOperatoriDavateliUslugi/?format=json
]
