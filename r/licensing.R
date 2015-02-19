# You may need to `setwd('~/path/to/inventory/r')`
library(ggplot2)
library(reshape2)
library(scales)
source('includes/constants.R')
source('includes/human.R')
source('includes/database.R')

# Get the unspecified and underspecified license usage per catalog.
q <- "
SELECT division_id, COUNT(
    CASE
      WHEN license = ''
        OR license LIKE 'http://example.com/other%'
        OR license LIKE 'http://example.com/notspecified%'
      THEN
        1
    END)
  FROM inventory_dataset
  GROUP BY division_id
  ORDER BY division_id
"
rows <- dbGetQuery(connection, q)
rows <- rows[!rows$division_id %in% subnational,]

# Get the denominator.
q <- "
SELECT division_id, COUNT(*)
  FROM inventory_dataset
  GROUP BY division_id
  ORDER BY division_id
"
r <- dbGetQuery(connection, q)
r <- r[!rows$division_id %in% subnational,]

# Change the counts to ratios.
rows$count <- rows$count / r$count

m <- melt(rows, 'division_id')
# Exclude catalogs without license metadata.
m <- m[!m$division_id %in% c(
  'ocd-division/country:cl',
  'ocd-division/country:cr',
  'ocd-division/country:gh',
  # @todo Remove once initiative is not alpha.
  'ocd-division/country:tz'
),]
# Exclude catalogs with only specific licenses.
m <- m[m$value>0,]

m$division_id <- human_division_ids(m$division_id)
m <- transform(m, division_id=reorder(division_id, value))

# Draw the plot for the report.
ggplot(data=m, aes(x=division_id, y=value)) + geom_bar(stat='identity') + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_continuous(labels=percent) + coord_flip()



# Global license usage.
# @note Includes subnational catalogs if scraped!
q <- "
SELECT license, COUNT(*)
  FROM inventory_dataset
  GROUP BY license
"
rows <- dbGetQuery(connection, q)

# Collapse unspecified and blank licenses into one.
rows[rows$license=='http://example.com/notspecified',]$count <- rows[rows$license=='http://example.com/notspecified',]$count + rows[rows$license=='',]$count
rows <- rows[rows$license!='',]

# Only display popular licenses.
m <- rows[rows$count>=500,]

m$license <- human_licenses(m$license)
m <- transform(m, license=reorder(license, count))

# Draw the plot for exploration.
ggplot(data=m, aes(x=license, y=count)) + geom_bar(stat='identity') + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_sqrt() + coord_flip()
