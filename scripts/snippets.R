library(ggplot2)
library(plyr)
library(reshape2)
library(RPostgreSQL)
library(scales)

# @see https://code.google.com/p/rpostgresql/
con <- dbConnect(dbDriver('PostgreSQL'), dbname='inventory')

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

country_names <- function (l) {
  return(revalue(l, c(
    'ocd-division/country:ar'='Argentina',
    'ocd-division/country:au'='Australia',
    'ocd-division/country:br'='Brazil',
    'ocd-division/country:ca'='Canada',
    'ocd-division/country:cl'='Chile',
    'ocd-division/country:cr'='Costa Rica',
    'ocd-division/country:ee'='Estonia',
    'ocd-division/country:es'='Spain',
    'ocd-division/country:fi'='Finland',
    'ocd-division/country:fr'='France',
    'ocd-division/country:gb'='United Kingdom',
    'ocd-division/country:gh'='Ghana',
    'ocd-division/country:gr'='Greece',
    'ocd-division/country:id'='Indonesia',
    'ocd-division/country:ie'='Ireland',
    'ocd-division/country:it'='Italy',
    'ocd-division/country:ke'='Kenya',
    'ocd-division/country:md'='Moldova',
    'ocd-division/country:mx'='Mexico',
    'ocd-division/country:nl'='Netherlands',
    'ocd-division/country:ph'='Philippines',
    'ocd-division/country:py'='Paraguay',
    'ocd-division/country:ro'='Romania',
    'ocd-division/country:se'='Sweden',
    'ocd-division/country:sk'='Slovakia',
    'ocd-division/country:tz'='Tanzania',
    'ocd-division/country:us'='United States',
    'ocd-division/country:uy'='Uruguay'
  )))
}



# Catalog structure

q <- "SELECT p.id, p.division_id, COUNT(*) from inventory_dataset p INNER JOIN inventory_distribution r ON r.dataset_id = p.id GROUP BY p.id"
rows <- dbGetQuery(con, q)

# Get the statistics.
mean(rows$count)
sd(rows$count)

rows <- rows[!rows$division_id %in% subnational,]

# Draw the boxplot of distributions per dataset.
rows$division_id <- country_names(rows$division_id)
rows$id <- NULL

ggplot(data=rows, aes(x=division_id, y=count)) + geom_boxplot(outlier.size=0) + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + coord_flip(ylim=c(0, 21)) # hardcode



# Metadata elements

width <- 575

dataset_fields <- list(
  c('title', "title != ''")
, c('identifier', "identifier != ''")
, c('issued', "issued IS NOT NULL")
, c('publisher', "publisher != ''")
, c('modified', "modified IS NOT NULL")
, c('description', "description != ''")
, c('keyword', "keyword IS NOT NULL AND keyword != '{}'")
, c('contactPoint', "\"contactPoint\" != ''")
, c('landingPage', "\"landingPage\" != ''")
, c('spatial', "spatial != ''")
, c('accrualPeriodicity', "\"accrualPeriodicity\" != ''")
, c('language', "language != ''")
, c('theme', "theme IS NOT NULL AND theme != '{}'")
, c('temporal', "temporal != ''")
)

distribution_fields <- list(
  c('accessURL', "\"accessURL\" != ''")
, c('issued', "issued IS NOT NULL")
, c('title', "title != ''")
, c('format', "format != ''")
, c('description', "description != ''")
  # To get the count before normalization
, c('mediaType', "mimetype != '' OR (division_id = 'ocd-division/country:ke' AND \"mediaType\" != '')")
, c('byteSize', "\"byteSize\" IS NOT NULL")
, c('modified', "modified IS NOT NULL")
)



# Global dataset metadata element usage.
# Get the denominator.
q <- "SELECT COUNT(*) FROM inventory_dataset"
rows <- dbGetQuery(con, q)
count <- rows$count
rows$count <- NULL

# Get the element usage.
for (field in dataset_fields) {
  q <- paste("SELECT COUNT(*) FROM inventory_dataset WHERE", field[2])
  rows[field[1]] <- dbGetQuery(con, q)$count / count
}

# Sort the data.
rows$id <- ''
m <- melt(rows, 'id')
m <- transform(m, variable=reorder(variable, value))

# Draw the bars.
ggplot(data=m, aes(x=variable, y=value)) + geom_bar(stat='identity', width=.75) + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_continuous(labels=percent) + coord_flip()



# Global distribution metadata element usage.
# Get the denominator.
q <- "SELECT COUNT(*) FROM inventory_distribution"
rows <- dbGetQuery(con, q)
count <- rows$count
rows$count <- NULL

# Get the element usage.
for (field in distribution_fields) {
  q <- paste("SELECT COUNT(*) FROM inventory_distribution WHERE", field[2])
  rows[field[1]] <- dbGetQuery(con, q)$count / count
}

# Sort the data.
rows$id <- ''
m <- melt(rows, 'id')
m <- transform(m, variable=reorder(variable, value))

# Draw the bars.
ggplot(data=m, aes(x=variable, y=value)) + geom_bar(stat='identity', width=.75) + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_continuous(labels=percent) + coord_flip()



# Per-catalog dataset metadata element usage.
# Get the denominator.
q <- "SELECT division_id, COUNT(*) FROM inventory_dataset GROUP BY division_id ORDER BY division_id"
rows <- dbGetQuery(con, q)
count <- rows$count

# Get the element usage per catalog.
for (field in dataset_fields) {
  q <- paste("SELECT division_id, COUNT(case when", field[2], "then 1 end) FROM inventory_dataset GROUP BY division_id ORDER BY division_id")
  rows[field[1]] <- dbGetQuery(con, q)$count / count
}

rows <- rows[!rows$division_id %in% subnational,]
rows$count <- NULL
m <- melt(rows, 'division_id')

# Draw the bars.
m$division_id <- country_names(m$division_id)

png('~/Downloads/metadata-datasets.png', width=width, height=width * 1.5)
ggplot(data=m, aes(x=variable, y=value)) + geom_bar(stat='identity') + theme(
  axis.text.x=element_text(angle=45, hjust=1),
  axis.title.x=element_blank(),
  axis.text.y=element_blank(),
  axis.ticks.y=element_blank(),
  axis.title.y=element_blank(),
  strip.text.y=element_text(angle=0)
) + facet_grid(division_id ~ .)
dev.off()



# Per-catalog distribution metadata element usage.
# Get the denominator.
q <- "SELECT division_id, COUNT(*) FROM inventory_distribution GROUP BY division_id ORDER BY division_id"
rows <- dbGetQuery(con, q)
count <- rows$count

# Get the element usage per catalog.
for (field in distribution_fields) {
  q <- paste("SELECT division_id, COUNT(case when", field[2], "then 1 end) FROM inventory_distribution GROUP BY division_id ORDER BY division_id")
  rows[field[1]] <- dbGetQuery(con, q)$count / count
}

rows <- rows[!rows$division_id %in% subnational,]
rows$count <- NULL
m <- melt(rows, 'division_id')

# Draw the bars.
m$division_id <- country_names(m$division_id)

png('~/Downloads/metadata-distributions.png', width=width, height=width * 1.5)
ggplot(data=m, aes(x=variable, y=value)) + geom_bar(stat='identity') + theme(
  axis.text.x=element_text(angle=45, hjust=1),
  axis.title.x=element_blank(),
  axis.text.y=element_blank(),
  axis.ticks.y=element_blank(),
  axis.title.y=element_blank(),
  strip.text.y=element_text(angle=0)
) + facet_grid(division_id ~ .)
dev.off()



# Media types

width <- 575

q <- "SELECT \"mediaType\", COUNT(*) FROM inventory_distribution WHERE \"mediaType\" != '' GROUP BY \"mediaType\""
rows <- dbGetQuery(con, q)
rows <- transform(rows, mediaType=reorder(mediaType, count))

media_types <- function (l) {
  return(revalue(l, c(
    'application/dbf'='DBF',
    'application/gml+xml'='GML',
    'application/gzip'='GZIP',
    'application/json'='JSON',
    'application/msword'='Word',
    'application/pdf'='PDF',
    'application/rdf+xml'='RDF/XML',
    'application/rss+xml'='RSS',
    'application/vnd.google-earth.kml+xml'='KML',
    'application/vnd.google-earth.kmz'='KMZ',
    'application/vnd.ms-excel'='Excel',
    'application/vnd.oasis.opendocument.spreadsheet'='ODS',
    'application/vnd.ogc.wms_xml'='WMS',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'='Excel 2007',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'='Word 2007',
    'application/x-ascii-grid'='ASCII GRID',
    'application/x-filegdb'='Esri file geodatabase',
    'application/x-hdf'='HDF',  # Hierarchical Data Format
    'application/x-msaccess'='Access',
    'application/x-msdownload'='Windows executable',
    'application/x-netcdf'='NetCDF',
    'application/x-pc-axis'='PC-Axis',
    'application/x-segy'='SEG-Y',
    'application/x-shapefile'='Shapefile',
    'application/x-tar'='TAR',
    'application/x-worldfile'='World file',
    'application/xhtml+xml'='XHTML',
    'application/xml'='XML',
    'application/zip'='ZIP',
    'audio/basic'='Audio',
    'chemical/x-xyz'='XYZ',
    'image/gif'='GIF',
    'image/jp2'='JPEG 2000',
    'image/jpeg'='JPEG',
    'image/tiff'='TIFF',
    'image/x-cdr'='CorelDRAW',
    'text/csv'='CSV',
    'text/html'='HTML',
    'text/n3'='N3',
    'text/plain'='Plain text',
    'text/turtle'='Turtle'
  )))
}

m <- rows[rows$count>=100,]
m$mediaType <- media_types(m$mediaType)

png('~/Downloads/media-types.png', width=width, height=width * 1.5)
ggplot(data=m, aes(x=mediaType, y=count)) + geom_bar(stat='identity') + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_sqrt() + coord_flip()
dev.off()


# Licenses

exclude <- c(
  # Alpha.
  'ocd-division/country:tz',

  # No license metadata.
  'ocd-division/country:cl',
  'ocd-division/country:cr',
  'ocd-division/country:gh'
)

# Get the denominator.
q <- "SELECT division_id, COUNT(*) FROM inventory_dataset GROUP BY division_id ORDER BY division_id"
rows <- dbGetQuery(con, q)
count <- rows$count
rows$count <- NULL

# Get the unspecified and underspecified license usage per catalog.
q <- "SELECT division_id, COUNT(case when license = '' OR license LIKE 'http://example.com/other%' OR license LIKE 'http://example.com/notspecified%' then 1 end) FROM inventory_dataset GROUP BY division_id ORDER BY division_id"
rows$license <- dbGetQuery(con, q)$count / count

m <- melt(rows, 'division_id')
m <- m[!m$division_id %in% subnational,]
m <- m[!m$division_id %in% exclude,]
m <- m[m$value>0,]
m <- transform(m, division_id=reorder(division_id, value))

# Draw the bars.
m$division_id <- country_names(m$division_id)
m$variable <- NULL

ggplot(data=m, aes(x=division_id, y=value)) + geom_bar(stat='identity') + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_continuous(labels=percent) + coord_flip()



# Global license usage.
q <- "SELECT license, COUNT(*) FROM inventory_dataset GROUP BY license"
rows <- dbGetQuery(con, q)
rows[rows$license=='http://example.com/notspecified',]$count <- rows[rows$license=='http://example.com/notspecified',]$count + rows[rows$license=='',]$count
rows <- rows[rows$license!='',]
rows <- transform(rows, license=reorder(license, count))

license_ids <- function (l) {
  return(revalue(l, c(
    'http://creativecommons.org/licenses/by/'='CC-BY',
    'http://creativecommons.org/licenses/by/3.0/au/'='CC-BY-3.0-AU',
    'http://creativecommons.org/licenses/by/3.0/es'='CC-BY-3.0-ES',
    'http://creativecommons.org/licenses/by/3.0/it/'='CC-BY-3.0-IT',
    'http://creativecommons.org/licenses/by/4.0/'='CC-BY-4.0',
    'http://creativecommons.org/publicdomain/mark/1.0/'='Public Domain',
    'http://creativecommons.org/publicdomain/zero/1.0/'='CC0-1.0',
    'http://data.gc.ca/eng/open-government-licence-canada'='OGL-Canada-2.0',
    'http://data.gov.md/en/terms-and-conditions'='Moldova',
    'http://example.com/notspecified'='N/A',
    'http://opendata.aragon.es/terminos'='Aragon',
    'http://opendatacommons.org/licenses/by/1.0/'='ODC-BY-1.0',
    'http://www.cis.es/cis/opencms/ES/2_bancodatos/Productos.html'='CIS',
    'http://www.dati.gov.it/iodl/2.0/'='IODL-2.0',
    'http://www.nationalarchives.gov.uk/doc/open-government-licence/'='OGL-UK-3.0'
  )))
}

m <- rows[rows$count>=500,]
m$license <- license_ids(m$license)
ggplot(data=m, aes(x=license, y=count)) + geom_bar(stat='identity') + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_sqrt() + coord_flip()
