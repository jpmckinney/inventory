library(RPostgreSQL)

# @see https://code.google.com/p/rpostgresql/
connection <- dbConnect(dbDriver('PostgreSQL'), dbname='inventory')
