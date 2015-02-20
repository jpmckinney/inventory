# Sorted by global usage.
dataset_fields <- list(
  c('title', "title != ''"),
  c('identifier', "identifier != ''"),
  c('issued', "issued IS NOT NULL"),
  c('publisher', "publisher != ''"),
  c('modified', "modified IS NOT NULL"),
  c('description', "description != ''"),
  c('keyword', "keyword IS NOT NULL AND keyword != '{}'"),
  c('contactPoint', "\"contactPoint\" != ''"),
  c('landingPage', "\"landingPage\" != ''"),
  c('spatial', "spatial != ''"),
  c('accrualPeriodicity', "\"accrualPeriodicity\" != ''"),
  c('language', "language != ''"),
  c('theme', "theme IS NOT NULL AND theme != '{}'"),
  c('temporal', "temporal != ''")
)

# Sorted by global usage.
distribution_fields <- list(
  c('accessURL', "\"accessURL\" != ''"),
  c('issued', "issued IS NOT NULL"),
  c('title', "title != ''"),
  c('format', "format != ''"),
  c('description', "description != ''"),
  # To get the count before normalize.py is run.
  c('mediaType', "mimetype != ''"),
  c('byteSize', "\"byteSize\" IS NOT NULL"),
  c('modified', "modified IS NOT NULL")
)

media_type_groups <- list(
  list('Documents', c(
    'application/msword',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/xhtml+xml',
    'text/html'
  )),
  list('Images', c(
    'image/gif',
    'image/jp2',
    'image/jpeg',
    'image/tiff',
    'image/x-cdr'
  )),
  list('Geospatial', c(
    'application/gml+xml',
    'application/vnd.google-earth.kml+xml',
    'application/vnd.google-earth.kmz',
    'application/vnd.ogc.wms_xml',
    'application/x-ascii-grid',
    'application/x-filegdb',
    'application/x-shapefile',
    'application/x-worldfile'
  )),
  list('Archives', c(
    'application/gzip',
    'application/x-msdownload',
    'application/x-tar',
    'application/zip'
  )),
  list('Generic', c(
    'application/json',
    'application/rss+xml',
    'application/xml',
    'text/plain'
  )),
  list('Tabular', c(
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.oasis.opendocument.spreadsheet',
    'application/x-msaccess',
    'application/dbf'
  )),
  list('Scientific', c(
    'application/x-netcdf',
    'application/x-pc-axis',
    'chemical/x-xyz',
    'application/x-segy',
    'application/x-hdf'
  )),
  list('Linked data', c(
    'text/turtle',
    'application/rdf+xml',
    'text/n3'
  ))
)

# Sorted by global usage within each grouping.
geospatial_media_types <- c(
  # Images
  'image/tiff',
  'image/jp2',

  # Geospatial
  'application/x-shapefile',
  'application/x-worldfile',
  'application/gml+xml',
  'application/vnd.google-earth.kmz',
  'application/vnd.google-earth.kml+xml',
  'application/vnd.ogc.wms_xml',
  'application/x-filegdb',
  'application/x-ascii-grid',

  # Tabular
  'application/dbf',
  'application/x-msaccess'

  # Documents
  # application/pdf matches too many.
  # Archives
  # application/zip matches too many.
  # Generic
  # application/json and application/xml match too many, in some catalogs.
  # Scientific
  # application/x-netcdf matches too many in US.
)

# Exclude subnational catalogs from national statistics.
subnational <- c(
  'ocd-division/country:ca/csd:2443027',
  'ocd-division/country:ca/csd:2466023',
  'ocd-division/country:ca/csd:3506008',
  'ocd-division/country:ca/csd:4611040',
  'ocd-division/country:ca/csd:4811052',
  'ocd-division/country:ca/csd:4811061',
  'ocd-division/country:ca/csd:5915001',
  'ocd-division/country:ca/csd:5915004',
  'ocd-division/country:ca/csd:5915007'
)
