# You may need to `setwd('~/path/to/inventory/r')`
library(ggplot2)
library(reshape2)
source('includes/constants.R')
source('includes/human.R')
source('includes/database.R')

width <- 575
quote <- function(l) lapply(l, function(x) paste("'", x, "'", sep=''))

# Global media type usage.
# @note Includes subnational catalogs if scraped!
q <- "
SELECT \"mediaType\", COUNT(*)
  FROM inventory_distribution
  WHERE \"mediaType\" != ''
  GROUP BY \"mediaType\""
rows <- dbGetQuery(connection, q)

# Only display popular media types.
m <- rows[rows$count>=100,]

m$mediaType <- human_media_types(m$mediaType)
m <- transform(m, mediaType=reorder(mediaType, count))

# Draw the plot for the report.
png('~/Downloads/media-types.png', width=width, height=width * 1.5)
ggplot(data=m, aes(x=mediaType, y=count)) + geom_bar(stat='identity') + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_sqrt() + coord_flip()
dev.off()



# Get the denominator.
q <- paste("
SELECT division_id, COUNT(*)
  FROM inventory_distribution
  WHERE \"mediaType\" IN (", paste(quote(geospatial_media_types), collapse=', '), ")
  GROUP BY division_id
  HAVING COUNT(*) >= 20
  ORDER BY division_id
")
rows <- dbGetQuery(connection, q)

# Get the geospatial media type usage per catalog.
for (media_type in geospatial_media_types) {
  q <- paste("
    SELECT division_id, COUNT(CASE WHEN \"mediaType\" = '", media_type, "' THEN 1 END)
      FROM inventory_distribution
      WHERE division_id IN (", paste(quote(rows$division_id), collapse=', ') ,")
      GROUP BY division_id
      ORDER BY division_id", sep='')
  rows[media_type] <- dbGetQuery(connection, q)$count / rows$count
}

rows <- rows[!rows$division_id %in% subnational,]
rows$count <- NULL

m <- melt(rows, 'division_id')

m$division_id <- human_division_ids(m$division_id)
m$variable <- human_media_types(m$variable)

# Draw the plot for the report.
png('~/Downloads/media-types.png', width=width, height=width * 1.5)
ggplot(data=m, aes(x=variable, y=value)) + geom_bar(stat='identity') + theme(
  axis.title.x=element_blank(),
  axis.text.y=element_blank(),
  axis.ticks.y=element_blank(),
  axis.title.y=element_blank(),
  strip.text.y=element_text(angle=0)
) + scale_y_sqrt() + facet_grid(division_id ~ .)
dev.off()



# CSV validation
# @note Includes subnational catalogs if scraped!
q <- "
SELECT UNNEST(errors) error, COUNT(*)
  FROM inventory_distribution
  WHERE valid = False
    AND \"mediaType\" = 'text/csv'
    AND http_content_type = 'text/csv'
    AND http_status_code = 200
  GROUP BY error
"
rows <- dbGetQuery(connection, q)

q <- "
SELECT COUNT(*)
  FROM inventory_distribution
  WHERE valid = False
    AND \"mediaType\" = 'text/csv'
    AND http_content_type = 'text/csv'
    AND http_status_code = 200
"
count <- dbGetQuery(connection, q)$count

m <- rows[rows$count>=25,]

m$count <- m$count / count

# Ignore `title_row`, because it has a bug.
# @see https://github.com/theodi/csvlint.rb/issues/100
# Ignore `undeclared_header`. CSVLint assumes a header if the Content-Type is
# "text/csv", instead of checking for a "header" parameter in all cases.
m <- m[!m$error=='title_row',]
m <- m[!m$error=='undeclared_header',]

m$error <- human_errors(m$error)
m <- transform(m, error=reorder(error, count))

ggplot(data=m, aes(x=error, y=count)) + geom_bar(stat='identity') + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_continuous(labels=percent) + coord_flip()



# CSV encoding
# @note Includes subnational catalogs if scraped!
q <- "
SELECT UPPER(http_charset), COUNT(*)
  FROM inventory_distribution
  WHERE \"mediaType\" = 'text/csv'
    AND http_content_type = 'text/csv'
    AND http_status_code = 200
  GROUP BY upper
"
rows <- dbGetQuery(connection, q)

q <- "
SELECT COUNT(*)
  FROM inventory_distribution
  WHERE \"mediaType\" = 'text/csv'
    AND http_content_type = 'text/csv'
    AND http_status_code = 200
"
count <- dbGetQuery(connection, q)$count

m <- rows

m$count <- m$count / count

m <- transform(m, upper=reorder(upper, count))

ggplot(data=m, aes(x=upper, y=count)) + geom_bar(stat='identity') + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_continuous(labels=percent) + coord_flip()
