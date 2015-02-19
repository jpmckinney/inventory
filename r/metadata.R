# You may need to `setwd('~/path/to/inventory/r')`
library(ggplot2)
library(reshape2)
library(scales)
source('includes/constants.R')
source('includes/human.R')
source('includes/database.R')

width <- 575

# Get the denominator.
# @note Includes subnational catalogs if scraped!
q <- "
SELECT COUNT(*)
  FROM inventory_dataset"
rows <- dbGetQuery(connection, q)

# Get the dataset metadata element usage.
for (field in dataset_fields) {
  q <- paste("
    SELECT COUNT(*)
      FROM inventory_dataset
      WHERE", field[2])
  rows[field[1]] <- dbGetQuery(connection, q)$count / rows$count
}

rows$count <- NULL
rows$id <- '' # dummy value

m <- melt(rows, 'id')

m <- transform(m, variable=reorder(variable, value))

# Draw the plot for the report.
ggplot(data=m, aes(x=variable, y=value)) + geom_bar(stat='identity', width=.75) + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_continuous(labels=percent) + coord_flip()



# Get the denominator.
q <- "
SELECT COUNT(*)
  FROM inventory_distribution"
rows <- dbGetQuery(connection, q)

# Get the distribution metadata element usage.
for (field in distribution_fields) {
  q <- paste("
    SELECT COUNT(*)
      FROM inventory_distribution
      WHERE", field[2])
  rows[field[1]] <- dbGetQuery(connection, q)$count / rows$count
}

rows$count <- NULL
rows$id <- '' # dummy value

m <- melt(rows, 'id')

m <- transform(m, variable=reorder(variable, value))

# Draw the plot for the report.
ggplot(data=m, aes(x=variable, y=value)) + geom_bar(stat='identity', width=.75) + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + scale_y_continuous(labels=percent) + coord_flip()



# Get the denominator.
q <- "
SELECT division_id, COUNT(*)
  FROM inventory_dataset
  GROUP BY division_id
  ORDER BY division_id"
rows <- dbGetQuery(connection, q)

# Get the dataset metadata element usage per catalog.
for (field in dataset_fields) {
  q <- paste("
    SELECT division_id, COUNT(CASE WHEN", field[2], "THEN 1 END)
      FROM inventory_dataset
      GROUP BY division_id
      ORDER BY division_id")
  rows[field[1]] <- dbGetQuery(connection, q)$count / rows$count
}

rows <- rows[!rows$division_id %in% subnational,]
rows$count <- NULL

m <- melt(rows, 'division_id')

m$division_id <- human_division_ids(m$division_id)

# Draw the plot for the report.
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



# Get the denominator.
q <- "
SELECT division_id, COUNT(*)
  FROM inventory_distribution
  GROUP BY division_id
  ORDER BY division_id"
rows <- dbGetQuery(connection, q)

# Get the distribution metadata element usage per catalog.
for (field in distribution_fields) {
  q <- paste("
    SELECT division_id, COUNT(CASE WHEN", field[2], "THEN 1 END)
      FROM inventory_distribution
      GROUP BY division_id
      ORDER BY division_id")
  rows[field[1]] <- dbGetQuery(connection, q)$count / rows$count
}

rows <- rows[!rows$division_id %in% subnational,]
rows$count <- NULL

m <- melt(rows, 'division_id')

m$division_id <- human_division_ids(m$division_id)

# Draw the plot for the report.
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
