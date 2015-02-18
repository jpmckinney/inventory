require 'set'
require 'timeout'
require 'uri'

require 'csvlint'

# Avoid double-encoding "%". Escape square brackets.
UNSAFE = Regexp.new("[^#{URI::PATTERN::UNRESERVED}#{URI::PATTERN::RESERVED}%]|\[|\]")

url = URI.escape(ARGV[0], UNSAFE)

options = {}

if ARGV.length > 1
  options['limitLines'] = ARGV[1].to_i
end

data = {
  valid: true,
  encoding: '',
  content_type: '',
  headers: '',
  errors: [],
}

Timeout.timeout(60) do # 1 min
  validator = Csvlint::Validator.new(url, options)

  data['encoding'] = validator.encoding
  data['content_type'] = validator.content_type
  data['headers'] = validator.headers

  errors = Set.new(validator.errors.map(&:type)) + validator.warnings.map(&:type)

  if errors.any?
    data['valid'] = false
    data['errors'] = errors.to_a
  end
end

puts JSON.dump(data)
