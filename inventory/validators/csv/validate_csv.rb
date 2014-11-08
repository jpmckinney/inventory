require 'set'

require 'csvlint'

validator = Csvlint::Validator.new(ARGV[0])

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
