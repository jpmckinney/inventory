# @todo This list must be continually updated.
urls = frozenset([
    ('ar', 'http://datospublicos.gob.ar/data/'),
    ('au', 'http://data.gov.au/'),
    ('br', 'http://dados.gov.br/'),
    ('ca', 'http://data.gc.ca/data/en/'),
    ('fr', 'http://data.gouv.fr/'),
    ('gb', 'http://data.gov.uk/'),
    ('id'  'http://data.id/'),
    ('ie', 'http://data.gov.ie/'),
    ('it', 'http://www.dati.gov.it/catalog/'),
    ('md', 'http://data.gov.md/'),
    ('mx', 'http://catalogo.datos.gob.mx/'),
    ('nl', 'https://data.overheid.nl/data/'),
    ('ph', 'http://data.gov.ph/catalogue/'),
    ('py', 'http://datos.gov.py/'),
    ('ro', 'http://data.gov.ro/'),
    ('se', 'http://oppnadata.se/'),
    ('sk', 'http://data.gov.sk/'),
    ('tz', 'http://opendata.go.tz/'),
    ('us', 'http://catalog.data.gov/'),
    ('uy', 'https://catalogodatos.gub.uy/'),
    # CKAN is hidden:
    # ('no', 'http://data.norge.no/'),
])
junar_urls = frozenset([
    ('cl', 'http://datos.gob.cl/'),
    ('cr', 'http://datosabiertos.gob.go.cr/'),
])
ogdi_urls = frozenset([
    ('mk', 'http://opendata.gov.mk/'),
    ('co', 'http://datos.gov.co/'),
])
opencolibri_urls = frozenset([
    ('gr', 'http://data.gov.gr/'),
])
socrata_urls = frozenset([
    ('ke', 'http://opendata.go.ke/'),
])
other_urls = frozenset([
    ('dk', 'http://data.digitaliser.dk/'),  # 757
    ('es', 'http://datos.gob.es/'),  # 2572
    ('fi', 'http://data.suomi.fi/'),  # <50
    ('ge', 'http://data.gov.ge/'),
    ('gh', 'http://data.gov.gh/'),  # 1068
    ('il', 'http://data.gov.il/'),
    ('jo', 'http://www.jordan.gov.jo/wps/portal/OpenData_en'),  # <100
    ('kr', 'https://www.data.go.kr/'),  # 9268
    ('lt', 'http://opendata.gov.lt/'),  # 262
    ('mt', 'http://data.gov.mt/'),  # 4
    ('nz', 'http://data.govt.nz/'),  # 2559
    ('tn', 'http://data.gov.tn/'),  # 133
    ('ua', 'http://data.gov.ua/'),  # 100
])

# APIs that respond to POST but not GET requests. No caching.
post_country_codes = frozenset([
    'nl',
])

# Core CKAN fields.
ckan_dataset_properties = frozenset([
    'author',
    'author_email',
    'creator_user_id',
    'extras',
    'groups',
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
    'num_resources',
    'num_tags',
    'organization',
    'owner_org',
    'private',
    'relationships_as_object',
    'relationships_as_subject',
    'resources',
    'revision_id',
    'revision_timestamp',
    'state',
    'tags',
    'title',
    'tracking_summary',
    'type',
    'url',
    'version',
])
ckan_distribution_properties = frozenset([
    'cache_last_updated',
    'cache_url',
    'created',
    'datastore_active',
    'description',
    'format',
    'hash',
    'id',
    'last_modified',
    'mimetype',
    'mimetype_inner',
    'name',
    'position',
    'resource_group_id',
    'resource_type',
    'revision_id',
    'revision_timestamp',
    'size',
    'state',
    'tracking_summary',
    'url',
    'url_type',
    'webstore_last_updated',
    'webstore_url',
])

# @see http://www.w3.org/TR/vocab-dcat/
dataset_properties = frozenset([
    'title',  # dct:title
    'notes',  # dct:description
    'metadata_created',  # dct:issued
    'metadata_modified',  # dct:modified
    'owner_org',  # dct:publisher
    'id',  # dct:identifier
    'tags',  # dcat:keyword
    'maintainer',  # vcard:fn
    'maintainer_email',  # vcard:hasEmail
    'author',  # vcard:fn
    'author_email',  # vcard:hasEmail
    'url',  # dcat:landingPage
])
distribution_properties = frozenset([
    'name',  # dct:title
    'description',  # dct:description
    'created',  # dct:issued
    'last_modified',  # dct:modified
    'url',  # dcat:accessURL
    'size',  # dcat:byteSize
    'mimetype',  # dcat:mediaType
    'format',  # dct:format
])
# CKAN doesn't have:
# * dct:language
# * dct:accrualPeriodicity
# * dct:spatial
# * dct:temporal
# * dcat:theme
# * dcat:downloadURL
#
# CKAN puts these on the dataset instead of on the distribution:
# * dct:license
# * dct:rights

license_properties = frozenset([
    'isopen',
    'license_title',
    'license_url',
])
license_extra_properties = frozenset([
    'licence_url',
    'access_constraints',
    'licence_url_title',
])

# These validations serve no substantive purpose, but may be used at a later date.
allowed_package_types = frozenset([
    'dataset',
    'harvest',
])
allowed_resource_types = frozenset([
    'api',
    'app',
    'data',
    'doc',
    'documentation',
    'download',
    'example',
    'file',
    'file.upload',
    'link',
    'metadata',
    'rss',
    'visualization',
    'FeatureClass esriGeometryPoint',
    'TOLOMEO:preset',
    'WMS',
])
