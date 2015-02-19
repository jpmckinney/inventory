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
  'application/x-ascii-grid',
  'application/vnd.google-earth.kml+xml',
  'application/x-filegdb',
  'application/vnd.ogc.wms_xml',

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
