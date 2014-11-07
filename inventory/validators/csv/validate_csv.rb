require 'csvlint'

if ARGV.length > 0
  url = ARGV.first.chomp
end

    opts = {
        "header" => true,
        "delimiter" => ","
    }

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

    json = output.to_json 
    puts json
