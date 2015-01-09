require 'csvlint'
require 'uri'
require 'set'
require 'timeout'

class Hash
  def to_utf8
    Hash[
      self.collect do |k, v|
        if (v.respond_to?(:to_utf8))
          [ k, v.to_utf8 ]
        elsif (v.respond_to?(:encoding))
          [ k, v.dup.force_encoding('UTF-8') ]
        else
          [ k, v ]
        end
      end
    ]
  end
end

nb_lines = 0

if ARGV.length == 0
  puts "Missing parameter URL for script"
else
  #url = URI.escape(URI.escape(ARGV[0]), '[]%')
  url = URI.escape(URI.escape(ARGV[0], '[]'), Regexp.new("[^#{URI::PATTERN::UNRESERVED}#{URI::PATTERN::RESERVED}%]"))
  #puts url
  if ARGV.length > 1
    nb_lines = ARGV[1].to_i
  end
end

opts = {}

if nb_lines > 0
  opts["limitLines"] = nb_lines
end

output = {}

begin
  #If something takes more that 1/2 an hour, we might skip it...
  complete_results = Timeout.timeout(18000) do      
  validator = Csvlint::Validator.new(url, opts)


  output['encoding'] = validator.encoding
  output['content_type'] = validator.content_type
  output['extension']    = validator.extension
  output['headers']      = validator.headers.to_utf8

  errors = Set.new(validator.errors.map(&:type)).merge(validator.warnings.map(&:type))

  if errors.any?
    output['valid'] = false
    output['errors'] = errors.to_a
  else   
    output['valid'] = true
    output['errors'] = Array.new   
  end
end
rescue Timeout::Error
  output['valid'] = false
  output['encoding'] = ''
  output['content_type'] = ''
  output['extension']    = ''
  output['headers']      = ''       
  output['errors'] = Array["time_out"]

rescue Exception => e
  output['valid'] = false
  output['encoding'] = ''
  output['content_type'] = ''
  output['extension']    = ''
  output['headers']      = ''
  output['errors'] = Array[e.message]  
end

puts output.to_json.dup.encode("UTF-8")


