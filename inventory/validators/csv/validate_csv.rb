require 'set'
require 'timeout'
require 'uri'

require 'csvlint'

# class Hash
#   def to_utf8
#     Hash[
#       self.collect do |k, v|
#         if (v.respond_to?(:to_utf8))
#           [ k, v.to_utf8 ]
#         elsif (v.respond_to?(:encoding))
#           [ k, v.dup.force_encoding('UTF-8') ]
#         else
#           [ k, v ]
#         end
#       end
#     ]
#   end
# end

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
  extension: '',
  headers: '',
  errors: []
}

begin
  Timeout.timeout(60) do # 1 min
    validator = Csvlint::Validator.new(url, options)
  end

  data['encoding'] = validator.encoding
  data['content_type'] = validator.content_type
  data['extension'] = validator.extension
  data['headers'] = validator.headers #.to_utf8

  errors = Set.new(validator.errors.map(&:type)) + validator.warnings.map(&:type)

  if errors.any?
    data['valid'] = false
    data['errors'] = errors.to_a
  end
rescue Timeout::Error
  data['valid'] = false
  data['errors'] = ['timeout']
rescue Exception => e
  data['valid'] = false
  data['errors'] = [e.message]
end

puts JSON.dumps(data)
