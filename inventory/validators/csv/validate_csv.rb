require 'csvlint'
require 'uri'

nb_lines = 0

if ARGV.length == 0
  puts "Missing parameter URL for script"
else
  url = URI.escape(URI.escape(ARGV.shift.chomp), '[]')
  if ARGV.length > 0
    nb_lines = ARGV.shift.to_i
  end
end

opts = {
    "header" => true,
    "delimiter" => ","
}

if nb_lines > 0
  opts["limitLines"] = nb_lines
end

validator = Csvlint::Validator.new(url, opts)
error_list = Array.new

if validator.errors.any? || validator.warnings.any? 

  validator.errors.each do |error|
    if not error_list.include? error.type 
      error_list << error.type
    end 
  end

  validator.warnings.each do |error|
    if not error_list.include? error.type
      error_list << error.type
    end
  end

  output = {}
  output["valid"] = false
  output["encoding"] = validator.encoding
  output["content_type"] = validator.content_type
  output["extension"] = validator.extension
  output["headers"] = validator.headers
  output["errors"] = error_list


else   
  output = {"valid" => true}

end

puts output.to_json 
