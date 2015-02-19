# coding: utf-8
require 'rubygems'
require 'bundler/setup'

require 'set'
require 'timeout'
require 'uri'

require 'csvlint'

OpenSSL::SSL::VERIFY_PEER = OpenSSL::SSL::VERIFY_NONE

# Avoid double-encoding "%". Escape square brackets.
UNSAFE = Regexp.new("[^#{URI::PATTERN::UNRESERVED}#{URI::PATTERN::RESERVED}%]|\[|\]")

url = URI.escape(ARGV[0], UNSAFE)

options = {}

if ARGV.length > 1
  options[:limit_lines] = ARGV[1].to_i
end

data = {
  valid: true,
  errors: [],
}

Timeout.timeout(60) do # 1 min
  validator = Csvlint::Validator.new(url, nil, nil, options)
  errors = Set.new(validator.errors.map(&:type)) + validator.warnings.map(&:type)
  if errors.any?
    data['valid'] = false
    data['errors'] = errors.to_a
  end
end

puts JSON.dump(data)
