# Catalog structure

library(ggplot2)
library(RPostgreSQL)

# @see https://code.google.com/p/rpostgresql/
con <- dbConnect(dbDriver('PostgreSQL'), dbname='inventory')
rs <- dbSendQuery(con, 'SELECT p.id, p.division_id, COUNT(*) from inventory_dataset p INNER JOIN inventory_distribution r ON r.dataset_id = p.id GROUP BY p.id')
rows <- fetch(rs, n=-1)

rows$id <- NULL
rows$division_id <- revalue(rows$division_id, c(
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
))

# Get the statistics.
mean(rows$count)
sd(rows$count)

# Produce the graph.
ggplot(data=rows, aes(x=division_id, y=count)) + geom_boxplot(outlier.size=0) + theme(axis.title=element_blank()) + coord_flip(ylim=c(0, 21)) # hardcode
