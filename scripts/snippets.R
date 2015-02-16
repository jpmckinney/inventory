library(plyr)
library(scales)

library(ggplot2)
library(RPostgreSQL)

# @see https://code.google.com/p/rpostgresql/
con <- dbConnect(dbDriver('PostgreSQL'), dbname='inventory')

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
    # 'ocd-division/country:fr'='France',
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

rows$division_id <- country_names(rows$division_id)
rows$id <- NULL

# Get the statistics.
mean(rows$count)
sd(rows$count)

# Draw the boxplot.
ggplot(data=rows, aes(x=division_id, y=count)) + geom_boxplot(outlier.size=0) + theme(
  axis.title=element_blank()
) + coord_flip(ylim=c(0, 21)) # hardcode



# Metadata elements

fields <- list(
  c('title', "title != ''"),
  c('identifier', "identifier != ''"),
  c('issued', "issued IS NOT NULL"),
  c('publisher', "publisher != ''"),
  c('modified', "modified IS NOT NULL"),
  c('description', "description != ''"),
  c('keyword', "keyword IS NOT NULL AND keyword != '{}'"),
  c('contactPoint', "\"contactPoint\" != ''"),
  c('landingPage', "\"landingPage\" != ''"),
  c('theme', "theme IS NOT NULL AND theme != '{}'"),
  c('language', "language != ''"),
  c('spatial', "spatial != ''"),
  c('temporal', "temporal != ''"),
  c('accrualPeriodicity', "\"accrualPeriodicity\" != ''")
)

q <- "SELECT COUNT(*) FROM inventory_dataset"
rows <- dbGetQuery(con, q)
count <- rows$count
rows$count <- NULL
rows$id <- ''

# Get the element usage.
for (field in fields) {
  q <- paste("SELECT COUNT(*) FROM inventory_dataset WHERE", field[2])
  rows[field[1]] <- dbGetQuery(con, q)$count / count
}

# Draw the bars.
m <- melt(rows, 'id')
m <- transform(m, variable=reorder(variable, value))
png('metadata.png', width=width, height=width * 1.5)
ggplot(data=m, aes(x=variable, y=value)) + geom_bar(stat='identity', width=.75) + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_continuous(labels=percent) + coord_flip()
dev.off()

q <- "SELECT division_id, COUNT(*) FROM inventory_dataset GROUP BY division_id ORDER BY division_id"
rows <- dbGetQuery(con, q)

# Get the dataset counts.
rows$division_id <- country_names(rows$division_id)
count <- rows$count
rows$count <- NULL

# Get the element usage per catalog.
for (field in fields) {
  q <- paste("SELECT division_id, COUNT(case when", field[2], "then 1 end) FROM inventory_dataset GROUP BY division_id ORDER BY division_id")
  rows[field[1]] <- dbGetQuery(con, q)$count / count
}

# Draw the bars.
width <- 575
png('metadata-catalogs.png', width=width, height=width * 1.5)
ggplot(data=melt(rows, 'division_id'), aes(x=variable, y=value)) + geom_bar(stat='identity') + theme(
  axis.text.x=element_text(angle=45, hjust=1),
  axis.title.x=element_blank(),
  axis.text.y=element_blank(),
  axis.ticks.y=element_blank(),
  axis.title.y=element_blank(),
  strip.text.y=element_text(angle=0)
) + facet_grid(division_id ~ .)
dev.off()
