library(plyr)

human_division_ids <- function (l) {
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

human_media_types <- function (l) {
  return(revalue(l, c(
    'application/dbf'='DBF',
    'application/gml+xml'='GML',
    'application/gzip'='GZIP',
    'application/json'='JSON',
    'application/msword'='Word',
    'application/pdf'='PDF',
    'application/rdf+xml'='RDF/XML',
    'application/rss+xml'='RSS',
    'application/vnd.geo+json'='GeoJSON',
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

human_licenses <- function (l) {
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

human_errors <- function (l) {
    return(revalue(l, c(
        # Errors
        'wrong_content_type'='The Content-Type header is not “text/csv”',
        'ragged_rows'='Rows have different numbers of columns',
        'blank_rows'='One or more rows is empty',
        'invalid_encoding'='Encoding error, e.g. invalid byte sequence',
        'not_found'='HTTP 404 status code',
        'stray_quote'='Stray quote character',
        'unclosed_quote'='Unclosed quoted field',
        'whitespace'='A quoted field has leading or trailing whitespace',
        'line_breaks'='The record delimiter is inconsistent',
        'undeclared_header'='The Content-Type header is missing a "header" parameter',

        # Warnings
        'no_encoding'='The Content-Type header is missing a "charset" parameter',
        'encoding'='The encoding is not UTF-8',
        'no_content_type'='The Content-Type header is missing',
        'excel'='The Content-Type header is missing and the file extension is .xls or .xlsx',
        'check_options'='The field delimiter is not a comma',
        'inconsistent_values'='One or more columns have inconsistent data types',
        'empty_column_name'='One or more columns have no name',
        'duplicate_column_name'='Two or more columns have the same name',
        'title_row'='The first row has fewer columns than the longest row'
    )))
}
