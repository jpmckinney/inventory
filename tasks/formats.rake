require_relative 'constants'

{ 'application/dbf' => [['dbf'], 'http://reference.wolfram.com/language/ref/format/DBF.html'],
  'application/json-l' => [['jsonl'], 'http://tools.ietf.org/html/draft-hallambaker-jsonl-01'],
  'application/n-triples' => [['nt'], 'http://www.w3.org/TR/n-triples/'],
  'application/owl+xml' => [['owl'], 'http://www.w3.org/TR/owl2-xml-serialization/'],
  'application/vnd.ogc.se_xml' => [nil, 'http://docs.geoserver.org/stable/en/user/services/wms/reference.html'],
  'application/vnd.ogc.wms_xml' => [nil, 'http://docs.geoserver.org/stable/en/user/services/wms/reference.html'],
  'application/x-ascii-grid' => [nil, 'http://inspire.ec.europa.eu/media-types/'],
  'application/x-esri-crs' => [['prj'], 'https://github.com/qgis/QGIS/blob/master/debian/mime/application'],
  'application/x-esri-shape' => [['shp', 'shx'], 'https://github.com/qgis/QGIS/blob/master/debian/mime/application'],
  'application/x-filegdb' => [nil, 'http://inspire.ec.europa.eu/media-types/'],
  'application/x-mapinfo-mif' => [['mif'], 'https://github.com/qgis/QGIS/blob/master/debian/mime/application'],
  'application/x-qgis-project' => [['qgs'], 'https://github.com/qgis/QGIS/blob/master/debian/mime/application'],
  'application/x-raster-ecw' => [['ecw'], 'https://github.com/qgis/QGIS/tree/master/debian/mime/application'],
  'application/x-sas' => [['sas'], 'http://support.sas.com/resources/papers/proceedings13/115-2013.pdf'],
  'application/x-shapefile' => [nil, 'http://inspire.ec.europa.eu/media-types/'],
  'application/x-tab' => [['tab'], 'http://inspire.ec.europa.eu/media-types/'],
  'application/x-worldfile' => [nil, 'http://inspire.ec.europa.eu/media-types/'],
  'image/x-mrsid' => [['sid'], 'http://en.wikipedia.org/wiki/MrSID'],
  'image/x-lwo' => [['lwo'], 'http://reference.wolfram.com/language/ref/format/LWO.html'],
}.each do |content_type,(extensions,reference)|
  MIME::Types.add(MIME::Type.new({
    'content-type' => content_type,
    'extensions' => extensions,
    'references' => reference,
  }))
end

{ 'application/marc' => 'marc',
  'application/msaccess' => 'accdb', # http://blogs.msdn.com/b/jaimer/archive/2008/01/04/mime-types.aspx
  'application/vnd.geo+json' => 'geojson',
}.each do |content_type,extension|
  type = MIME::Types[content_type][0]
  type.add_extensions(extension)
  MIME::Types.index_extensions(type)
end

namespace :ckan do
  namespace :formats do
    task :mappings do
      formats = []

      Dir['out/ckan/*.formats.json'].each do |f|
        JSON.load(File.read(f)).keys.each do |format|
          # Normalize case and spaces.
          format = format.downcase.gsub(/\p{Space}/, ' ').strip.squeeze(' ').
            # Remove punctuation prefixes.
            gsub(/\A\*?[\.\/] ?/, '').
            # Fix typos.
            sub(/\A(?:aplication|appication|applicaton)\b/, 'application').
            sub(/\Acsw\z/, 'csv').
            sub(/\Acv\z/, 'csv').
            sub(/\Ahml\z/, 'html').
            sub(/\Aklm\z/, 'kml').
            sub(/\Atxls\z/, 'xls').
            sub(/\Axl\z/, 'xls').
            sub(/\Axslx\z/, 'xlsx').
            # Fix typos in media types.
            sub(/\Atexl\b/, 'text').
            sub(/\Atxt\b/, 'text').
            sub(/\bcvs\b/, 'csv').
            sub(/\bhtm\b/, 'html').
            sub(/\bjpg\b/, 'jpeg').
            sub(/\btif\b/, 'tiff').
            # Replace semi-colon separator with slash.
            sub(/(?<=\S);(?=\S)/, '/')

          unless format[','] || NON_MEDIA_TYPES.include?(format) || UNKNOWN_MEDIA_TYPES.include?(format)
            if MIME::Types[format].empty? && MIME::Types.type_for(format).empty?
              test_format = format.sub(/\A(?:application|image|text)\//, '')
              test_format = MAPPINGS.fetch(format, format)
              if MIME::Types[test_format].empty? && MIME::Types.type_for(format).empty?
                formats << format
              end
            end
          end
        end
      end

      formats.uniq!
      puts formats.sort
      puts "#{formats.size} unrecognized formats"
    end
  end
end
