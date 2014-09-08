MAPPINGS = {
  'application/access' => 'application/x-msaccess',
  'application/excel' => 'application/vnd.ms-excel',
  'text/comma-separated-values' => 'text/csv',
}

# @see http://www.iana.org/assignments/media-types/media-types.xhtml
# @see http://blogs.msdn.com/b/vsofficedeveloper/archive/2008/05/08/office-2007-open-xml-mime-types.aspx
# @see http://blogs.msdn.com/b/jaimer/archive/2008/01/04/mime-types.aspx
CORRECTIONS = {
  'application/ms-excel'                     => 'application/vnd.ms-excel',
  'application/msexcel'                      => 'application/vnd.ms-excel',
  'application/octet-string'                 => 'application/octet-stream',
  'application/octet_stream'                 => 'application/octet-stream',
  'application/vnd.excel'                    => 'application/vnd.ms-excel',
  'application/vnd.ms-access'                => 'application/msaccess',
  'application/vnd.ms-excel.12'              => 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel.macroenabled.12' => 'application/vnd.ms-excel.sheet.macroEnabled.12',
  'application/vnd.ms-pkistl'                => 'application/vnd.ms-pki.stl',
  'application/vnd.ms-word'                  => 'application/msword',
  'application/vnd.msexcel'                  => 'application/vnd.ms-excel',
  'application/x-msexcel'                    => 'application/vnd.ms-excel',
  'application/x-mspowerpoint'               => 'application/vnd.ms-powerpoint',
  'application/x-zip-compressed'             => 'application/zip',
  'application/xml+rdf'                      => 'application/rdf+xml',
  'binary/octet-stream'                      => 'application/octet-stream',
  'image/geotiff'                            => 'image/tiff',

  '0_v2 / pdf'                                => 'application/pdf',
  'access'                                    => 'application/msaccess',
  'arcgis file geodatabase'                   => 'application/x-filegdb',
  'arcgis geodatabase'                        => 'application/x-filegdb',
  'arcgis grid format'                        => 'application/x-ascii-grid',
  'arcgis personal geodatabase'               => 'application/x-msaccess',
  'arcgis shapefile'                          => 'application/x-shapefile',
  'arcgrid'                                   => 'application/x-ascii-grid',
  'arcinfo grid'                              => 'application/x-ascii-grid',
  'arcinfo workstation grid'                  => 'application/x-ascii-grid',
  'ascii grid'                                => 'application/x-ascii-grid',
  'ascii'                                     => 'text/plain',
  'ascii-grid (arcinfo)'                      => 'application/x-ascii-grid',
  'atom 1.0'                                  => 'application/atom+xml',
  'aug 2014 / csv'                            => 'text/csv',
  'cdec ascii'                                => 'application/zip', # @see http://www.geobase.ca/geobase/en/data/cded/description.html
  'csv (inside zip)'                          => 'application/zip',
  'csv (zip)'                                 => 'application/zip',
  'csv / zip'                                 => 'application/zip',
  'csv(txt)'                                  => 'text/csv',
  'csv-semicolon delimited'                   => 'text/csv',
  'csv-tab delimited'                         => 'text/tab-separated-values',
  'csv/api'                                   => 'text/csv',
  'csv/txt'                                   => 'text/csv',
  'csv/utf8'                                  => 'text/csv',
  'csv/webservice/api'                        => 'text/csv',
  'dbase'                                     => 'application/dbf',
  'esri geodatabase feature class'            => 'application/x-filegdb',
  'esri grid'                                 => 'application/x-ascii-grid',
  'esri shape file'                           => 'application/x-shapefile',
  'esri shapefile'                            => 'application/x-shapefile',
  'excel (.xlsx)'                             => 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'excel (xlsx)'                              => 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'excel file'                                => 'application/vnd.ms-excel',
  'excel'                                     => 'application/vnd.ms-excel',
  'fgdb / gdb'                                => 'application/x-filegdb',
  'file geo-database (.gdb)'                  => 'application/x-filegdb',
  'file geodatabase'                          => 'application/x-filegdb',
  'fixed-length ascii text'                   => 'text/plain',
  'flash'                                     => 'video/x-flv',
  'ftp site with zipped esri file geodabases' => 'application/x-filegdb',
  'gdb (esri)'                                => 'application/x-filegdb',
  'geodatabase'                               => 'application/x-filegdb',
  'geopdf'                                    => 'application/pdf',
  'geotif'                                    => 'image/tiff',
  'geotiff'                                   => 'image/tiff',
  'grid esri'                                 => 'application/x-ascii-grid',
  'grid'                                      => 'application/x-ascii-grid',
  'gtfs'                                      => 'application/zip',
  'gzip'                                      => 'application/gzip',
  'html5'                                     => 'text/html',
  'icalendar'                                 => 'text/calendar',
  'jpeg (cc48)'                               => 'image/jpeg',
  'jpeg 2000'                                 => 'image/jp2',
  'jul 2014 / csv'                            => 'text/csv',
  'kml / kmz'                                 => 'application/vnd.google-earth.kmz',
  'kml/google maps'                           => 'application/vnd.google-earth.kml+xml',
  'kml/kmz'                                   => 'application/vnd.google-earth.kmz',
  'lzma'                                      => 'application/x-7z-compressed',
  'mif / mid'                                 => 'application/x-mapinfo-mif',
  'mif−mid'                                   => 'application/x-mapinfo-mif',
  'mrsid'                                     => 'image/x-mrsid',
  'ms dbase file'                             => 'application/dbf',
  'ms dbase table'                            => 'application/dbf',
  'msaccess'                                  => 'application/msaccess',
  'multi-page tiff'                           => 'image/tiff',
  'n-triple'                                  => 'application/n-triples',
  'nc(netcdf)'                                => 'application/x-netcdf',
  'netcdf'                                    => 'application/x-netcdf',
  'netcdf3'                                   => 'application/x-netcdf',
  'oai-pmh (xml repons)'                      => 'application/xml',
  'oai-pmh (xml respons)'                     => 'application/xml',
  'oai-pmh en sru (respons in xml)'           => 'application/xml',
  'oai-pmh'                                   => 'application/xml',
  'odata webservice'                          => 'application/json',
  'osm'                                       => 'application/xml', # @see http://wiki.openstreetmap.org/wiki/OSM_XML
  'personal geodatabase feature class'        => 'application/x-msaccess',
  'personal geodatabase'                      => 'application/x-msaccess',
  'plain'                                     => 'text/plain',
  'qgis'                                      => 'application/x-qgis-project',
  'raster data set (.grd)'                    => 'application/x-ascii-grid',
  'rdf/turtle'                                => 'text/turtle',
  'rss 1.0'                                   => 'application/rss+xml',
  'rss 2.0'                                   => 'application/rss+xml',
  'shape file'                                => 'application/x-shapefile',
  'shape'                                     => 'application/x-shapefile',
  'shapefile'                                 => 'application/x-shapefile',
  'shapefiler'                                => 'application/x-shapefile',
  'shp (cc47)'                                => 'application/x-shapefile',
  'shp (cc48)'                                => 'application/x-shapefile',
  'shp (l93)'                                 => 'application/x-shapefile',
  'shp (wgs84)'                               => 'application/x-shapefile',
  'shp / zip'                                 => 'application/x-shapefile',
  'single-page tiff'                          => 'image/tiff',
  'skos webservice'                           => 'application/rdf+xml',
  'text (csv)'                                => 'text/csv',
  'text(csv)'                                 => 'text/csv',
  'texte'                                     => 'text/plain',
  'tgrshp (compressed)'                       => 'application/x-shapefile',
  'tiff (cc48)'                               => 'image/tiff',
  'tiff world file'                           => 'application/x-worldfile',
  'turtle'                                    => 'text/turtle',
  'web browser display'                       => 'text/html',
  'web page'                                  => 'text/html',
  'web site'                                  => 'text/html',
  'web tool'                                  => 'text/html',
  'web-interface'                             => 'text/html',
  'webinterface'                              => 'text/html',
  'webpage'                                   => 'text/html',
  'website'                                   => 'text/html',
  'winzipped shapefile'                       => 'application/x-shapefile',
  'wms'                                       => 'application/vnd.ogc.wms_xml',
  'wms_xml'                                   => 'application/vnd.ogc.wms_xml',
  'word'                                      => 'application/msword',
  'xls via website'                           => 'application/vnd.ms-excel',
  'xml (atom)'                                => 'application/atom+xml',
  'xml osm'                                   => 'application/xml',
  'xml/kml/kmz'                               => 'application/vnd.google-earth.kmz',
  'xml: oai-pmh dublin core'                  => 'application/xml',
  'xsd'                                       => 'application/xml',
  'zip (csv utf8)'                            => 'application/zip',
  'zip (csv)'                                 => 'application/zip',
  'zip (pdf)'                                 => 'application/zip',
  'zip (shp)'                                 => 'application/x-shapefile',
  'zip (sql + jpeg)'                          => 'application/zip',
  'zip (sql)'                                 => 'application/zip',
  'zip / xml'                                 => 'application/zip',
  'zip file containing csv files'             => 'application/zip',
  'zip file containing multiple csv files.'   => 'application/zip',
  'zip | kml en json'                         => 'application/zip',
  'zip | shape-files + excel'                 => 'application/zip',
  'zip+csv'                                   => 'application/zip',
  'zip: spss'                                 => 'application/zip',
  'zip: xls'                                  => 'application/zip',
  'zip:gml'                                   => 'application/zip',
  'zip:json'                                  => 'application/zip',
  'zip:mdb'                                   => 'application/zip',
  'zip:shape'                                 => 'application/x-shapefile',
  'zip:xml en csv'                            => 'application/zip',
  'zip:xml'                                   => 'application/zip',
  'zipped esri file geodatabase'              => 'application/x-filegdb',
}

NON_MEDIA_TYPES = [
  # Download
  'application/force-download',
  'application/save',
  'application/x-download',
  'force-download',

  # Unknown
  'all',
  'application/unknown',
  'application/x-unknown-content-type',
  'n/a',
  'no-type',
  'unknown/unknown',

  # Other
  'altro', # IT
  'autre', # FR
  'other', # EN

  # Ambiguous
  '013',
  '014',
  'arcgis map preview',
  'arcgis online map',
  'cd-rom',
  'data file',
  'data',
  'database',
  'fichier tabulé',
  'geospatial',
  'image',
  'img',
  'raster digital data set',
  'vector digital data set (polygon)',
  'vector digital data set',

  # Multiple
  'csv ods pdf',
  'csv or kml',
  'csv vers pdf',
  'csv/txt; pdf',
  'csv/txt; sgml; xml',
  'csv/txt; xml; tiff',
  'dxf/dwg (cc48)',
  'dxf/dwg (l93)',
  'dxf/dwg (wgs84)',
  'kongsberg/simrad instrument files (.raw or .wcd)',
  'pdf/webpages',
  'png et svg',
  'sgml; xml; tiff',
  'xbrl (xml) + xls',
  'xls en csv',
  'xml; pdf',
  'xml; tiff',
  'variable',
  'varies',
  'varies upon user output',
  'various',
  'various formats',

  # API
  'api',
  'api/sparql',
  'api: xml en jpeg',
  'arcgis map service',
  'arcgis server rest',
  'arcgis server',
  'ensearch api',
  'esri rest',
  'feed google maps',
  'feed',
  'openxml',
  'rest',
  'service',
  'sparql',
  'wcs',
  'webservice',
  'wfs',
  'wmf & wfs',
  'wms & wfs',

  # Code
  'ashx',
  'asp',
  'aspx',
  'do',
  'jsp',

  # Non-file: Protocol
  'opendap',
  'xms enabled',

  # Non-file: Application
  'app',
  'cross-platform java-based desktop software',
  'map',
  'mobile application',
  'query tool',
  'tool',
  'widget',

  # Non-file: Other
  '15 kb',
  '4-byte floating point(binary) data.http://www.ncdc.noaa.gov/oa/rsad/ssmi/gridded/index.php?name=description',
  'http://reference.data.gov.uk/gov-structure/organogram/?pubbod=imperial-war-museums&post=dg',
  'it%2fit%2fareac%2f',
  "l'inventaire immobilier de l'état - rhone alpes",
  'upon request',
]

UNKNOWN_MEDIA_TYPES = [
  # @see http://en.wikipedia.org/wiki/CorelDRAW (.cdr)
  'cdr',
  # @see http://en.wikipedia.org/wiki/GRIB
  'grib1',
  # @see http://en.wikipedia.org/wiki/SEG_Y
  'segy',
  'raw knudsen seg-y datagram',
  # @see http://en.wikipedia.org/wiki/Shapefile
  'sbn',
  'sbx',
  # @see http://en.wikipedia.org/wiki/Spatial_Data_Transfer_Standard
  'sdts',
  # @see http://webhelp.esri.com/arcgisdesktop/9.3/index.cfm?TopicName=gridfloat
  'gridfloat',
  # @see http://webhelp.esri.com/arcgisexplorer/900/en/add_arcgis_layers.htm
  'layer package (lpk) for arcgis',
  'lyr',
  # @see http://wiki.openstreetmap.org/wiki/PBF_Format
  'pbf',
  # @see http://www.s-57.com/
  's57',
]
