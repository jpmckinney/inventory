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
  axis.title=element_blank()
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
