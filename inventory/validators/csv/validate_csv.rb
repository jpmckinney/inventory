require 'csvlint'

if ARGV.length > 0
  url = ARGV.first.chomp
end

opts = {
  'header' => true,
  'delimiter' => ','
}

validator = Csvlint::Validator.new(url, opts)
error_list = []

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

  output = {
    'valid'        => false,
    'encoding'     => validator.encoding,
    'content_type' => validator.content_type,
    'extension'    => validator.extension,
    'headers'      => validator.headers,
    'errors'       => error_list,
  }
else   
  output = {
    'valid' => true,
  }
end

puts output.to_json
