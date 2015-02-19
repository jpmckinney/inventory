# You may need to `setwd('~/path/to/inventory/r')`
library(ggplot2)
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
