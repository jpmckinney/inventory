require 'csvlint'
require 'uri'
require 'set'

nb_lines = 0

if ARGV.length == 0
  puts "Missing parameter URL for script"
else
  url = URI.escape(URI.escape(ARGV[0]), '[]')
  if ARGV.length > 1
    nb_lines = ARGV[1].to_i
  end
end

opts = {}

if nb_lines > 0
  opts["limitLines"] = nb_lines
end

validator = Csvlint::Validator.new(url, opts)

errors = Set.new(validator.errors.map(&:type)).merge(validator.warnings.map(&:type))

if errors.any?
  output = {
    'valid' => false,
    'encoding'     => validator.encoding,
    'content_type' => validator.content_type,
    'extension'    => validator.extension,
    'headers'      => validator.headers,
    'errors'       => errors.to_a,
  }
else   
  output = {
    'valid' => true,
  }
end

puts output.to_json 
