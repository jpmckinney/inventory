require 'csv'
require 'open-uri'
require 'uri'

require 'iso_country_codes'
require 'nokogiri'

HEADER_COUNTRY = 'Country'
HEADER_ISO_3166_1 = 'Code'
HEADER_OGP_URL = 'OGP URL'
HEADER_CATALOG_URL = 'Catalog URL'

def rows
  [].tap do |array|
    CSV.parse(open('https://docs.google.com/spreadsheets/d/1WPKcioIQ_lVlNgKGnXZYuGQMIwHi-EwBZLro4fHEDYU/export?gid=0&format=csv').read, headers: true) do |row|
      break unless row[HEADER_COUNTRY]
      array << row
    end
  end
end

desc 'Print major languages for each country'
task :languages do
  def text(element)
    element.text.
      gsub(/[(\[][^)\]]+[)\]]/, '').
      gsub(/\d+(?:\.\d+)?%+/, '').
      gsub(/\p{Space}+/, ' ').
      gsub(',', '').
      strip
  end

  rows.each do |row|
    languages = {}

    page = case row[HEADER_ISO_3166_1]
    when 'ge'
      'Georgia_(country)'
    when 'mk'
      'Republic_of_Macedonia'
    else
      row[HEADER_COUNTRY].gsub(' ', '_')
    end

    url = "https://en.wikipedia.org/wiki/#{page}"

    Nokogiri::HTML(open(url)).css('.infobox tr').each do |tr|
      cells = tr.css('th,td')
      if cells.size > 1
        cells.css('sup').remove
        label = text(cells[-2])
        if label[/language/i] && !['Indigenous language', 'Recognised regional languages', 'Regional languages', 'Vernacular languages'].include?(label)
          value = text(cells[-1])

          as = cells[-1].css('a')
          if as.size > 1 || as.any? && !text(as[0])[/\A[a-z]/]
            as.each do |a|
              language = text(a)
              unless language == 'Lingua franca'
                languages[language] ||= label
              end
            end
          else
            languages[value] ||= label
          end

          # Eastern, Northern, Southern, Liberian Kreyol, Tunisian Arabic, Ulster Scots, NS Sign Language
          others = value.split(/(?<!astern|rthern|uthern|berian|nisian|Ulster) /) - ['and', 'NZ', 'Sign', 'Language'] - languages.keys
          if others.any?
            joined = others.join(' ').strip
            unless ['11 languages', '68 native language groups are also legally recognized.', 'None at federal level', 'Regional languages'].include?(joined)
              others.each do |language|
                languages[language] ||= label
              end
            end
          end
        end
      end
    end

    width = 22

    puts "#{row[HEADER_COUNTRY].ljust(width + 2)} #{url}"
    if languages.size == 1
      puts "  #{languages.first[0]}"
    else
      languages.each do |language,label|
        puts "  #{language.ljust(width)} #{label}"
      end
    end
    puts
  end
end

namespace :catalogs do
  desc 'Guess missing catalogs'
  task :guess do
    rows.each do |row|
      unless row[HEADER_CATALOG_URL]
        if row[HEADER_COUNTRY] == 'South Korea'
          results = [IsoCountryCodes.find('KR')]
        else
          results = IsoCountryCodes.search_by_name(row[HEADER_COUNTRY])
        end

        if results.size == 1
          tld = results[0].alpha2.downcase
          puts tld
          %w(go gob gouv gov govt gub riik).each do |b|
            candidate = nil
            %w(dados data date datos datosabiertos opendata transparencia transparency transparenta).each do |a|
              url = URI.parse("http://#{a}.#{b}.#{tld}")
              begin
                Socket.gethostbyname(url.host) && open(url)
                if candidate
                  # If multiple subdomains work, it's a parked domain.
                  candidate = nil
                  break
                else
                  candidate = url
                end
              rescue SocketError, OpenURI::HTTPError
                # pass
              rescue => e
                puts "#{e.class}: #{e}"
              end
            end
            if candidate
              puts candidate
            end
          end
        else
          puts "#{row[HEADER_COUNTRY]} too many results"
        end
      end
    end
  end
end

namespace :commitments do
  desc 'Download action plans'
  task :plans do
    rows.each do |row|
      url = "#{row[HEADER_OGP_URL]}/action-plan"
      a = Nokogiri::HTML(open(url)).at_css('.views-field-field-country-ap-pdf a')
      if a
        basename = File.join('action-plans', "#{File.basename(row[HEADER_OGP_URL])}#{File.extname(a[:href])}")
        path = File.expand_path(basename, __dir__)
        if File.exist?(path)
          puts "Skipping #{row[HEADER_COUNTRY]} because #{basename} exists..."
        else
          puts "Downloading #{row[HEADER_COUNTRY]} to #{basename}..."
          File.open(path, 'w') do |f|
            f.write open(a[:href]).read
          end
        end
      else
        puts "#{url} action plan not found"
      end
    end
  end

  desc 'Print whether a country has open data commitments'
  task :tags do
    rows.each do |row|
      doc = Nokogiri::HTML(open(row[HEADER_OGP_URL]))
      if doc.at_css('.view-id-country_commitment_categories')
        puts !!doc.at_css('.tid-1196')
      else
        puts
      end
    end
  end

  desc 'Print the number of commitments'
  task :totals do
    rows.each do |row|
      puts Nokogiri::HTML(open(row[HEADER_OGP_URL])).at_css('.country-commitments-delivered').text.strip
    end
  end
end

namespace :census do
  desc 'Print Census scores'
  task :scores do
    data = JSON.load(open('http://national.census.okfn.org/overview.json').read)

    puts rows.map{|row|
      data['byplace'][row[HEADER_ISO_3166_1]]['score']
    }
  end

  desc 'Print Census sources'
  task :sources do
    data = JSON.load(open('http://national.census.okfn.org/overview.json').read)

    puts rows.map{|row|
      data['byplace'][row[HEADER_ISO_3166_1]]['datasets'].reduce([]) do |memo,(_,hash)|
        memo << URI.parse(hash['url']).host
      end.reject(&:nil?).map{|host| host.sub(/\Awww\./, '').ljust(35)}.uniq.join('')
    }
  end

  desc 'Print Census formats'
  task :formats do
    data = JSON.load(open('http://national.census.okfn.org/overview.json').read)

    puts rows.map{|row|
      data['byplace'][row[HEADER_ISO_3166_1]]['datasets'].reduce([]) do |memo,(_,hash)|
        memo += hash['format'].split(/[&,\/;]+| and /).reject do |format|
          format.empty? || [
            '...',
            'filling out a captcha',
            'Formats varies from open CSV ot PDF other non-machine readable formats',
            'Multiple',
            'multiple',
            'other machine readable',
            'other?',
          ].include?(format.strip)
        end.map do |format|
          format = format.sub('.', '').sub(/ \([^)]+\)/, '').sub(/ - .+/, '').sub(/\bmostly\b/, '').upcase.strip
          case format
          when 'TSV'
            'CSV'
          when 'DBF FILES'
            'DBF'
          when 'XLS'
            'EXCEL'
          when 'FIXED-WIDTH TEXT FILE'
            'FIXED WIDTH'
          when 'HTML TABLE', 'HTML TABLES', 'STRUCTURED HTML', 'HTML WITH EMBEDDED FRAMES THAT ONLY CAN BE ACCESSED SUBMITTING THE IDENTIFICATION NUMBER'
            'HTML'
          when 'JPEG'
            'JPG'
          when 'SHAPE', 'SHAPEFILE', 'SHAPEFILES', 'SHAPE FILES'
            'SHP'
          when 'TIF'
            'TIFF'
          when 'DOC'
            'WORD'
          else
            format
          end
        end
      end.uniq.sort.join(',')
    }
  end
end
