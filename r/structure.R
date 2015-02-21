# You may need to `setwd('~/path/to/inventory/r')`
library(ggplot2)
library(reshape2)
source('includes/constants.R')
source('includes/human.R')
source('includes/database.R')

# Get the number of distributions per dataset.
q <- "
SELECT p.id, p.division_id, COUNT(*)
  FROM inventory_dataset p
  INNER JOIN inventory_distribution r
    ON r.dataset_id = p.id
  GROUP BY p.id
"
rows <- dbGetQuery(connection, q)
rows <- rows[!rows$division_id %in% subnational,]

rows$division_id <- human_division_ids(rows$division_id)

# Draw the plot for the report.
ggplot(data=rows, aes(x=division_id, y=count)) + geom_boxplot(outlier.size=0) + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + coord_flip(ylim=c(0, 21))

# Get statistics for the report.
mean(rows$count)

sd(rows$count)



# Get the per-catalog classifications of access URL domain names.
rows <- read.csv('~/path/to/inventory/r/access.csv', header=TRUE)
colnames(rows)[1] <- 'division_id'
rows <- rows[!rows$division_id %in% subnational,]

rows[2:4] <- rows[2:4] / rows$count
rows$count <- NULL

m <- melt(rows, 'division_id')
m$division_id <- human_division_ids(m$division_id)

# Unused as too many catalogs contain subnational data.
ggplot(data=m, aes(x=division_id, y=value, fill=variable)) + geom_bar(stat='identity') + theme(
  axis.title=element_blank(),
  text=element_text(size=16)
) + coord_flip()



# Identify domains to add to the bottom of report.py.
rows <- read.csv('~/path/to/inventory/r/domains.csv', header=TRUE)
colnames(rows)[1] <- 'division_id'
rows <- rows[!rows$division_id %in% subnational,]

count <- rows$count
names(count) <- rows$division_id
rows$count <- NULL

m <- melt(rows, 'division_id')

summarize <- function (country_code, threshold=0.001) {
  division_id <- paste('ocd-division/country:', country_code, sep='')
  r <- na.omit(m[m$division_id==division_id,])
  return(r[r$value>=count[division_id]*threshold,])
}
