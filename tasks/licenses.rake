namespace :ckan do
  namespace :licenses do
    desc 'Check uniformity of license metadata'
    task :metadata do
      metadata = {}

      Dir['out/ckan/*.metadata_license.json'].each do |f|
        JSON.load(File.read(f)).each do |id,hash|
          metadata[id] ||= {
            'license_title' => Set.new,
            'license_url' => Set.new,
            'isopen' => Set.new,
          }
          hash.each do |key,value|
            metadata[id][key] << value
          end
        end
      end

      metadata.each do |id,hash|
        hash.each do |key,value|
          if metadata[id][key].size < 2
            metadata[id].delete(key)
          else
            metadata[id][key] = value.to_a
          end
        end
        if metadata[id].empty?
          metadata.delete(id)
        end
      end

      puts JSON.pretty_generate(metadata)
    end

    desc 'List licenses'
    task :list do
      totals = {}

      Dir['out/ckan/*.metadata_dataset.json'].each do |f|
        id = File.basename(f)[/\A[a-z]+/]
        data = JSON.load(File.read(f))
        data.delete('extras')
        totals[id] = data.values.max.to_f
      end

      results = {}

      Dir['out/ckan/*.licenses.json'].each do |f|
        id = File.basename(f)[/\A[a-z]+/]
        data = JSON.load(File.read(f))

        result = {}
        remainder = 1
        data.each do |key,value|
          quotient = value / totals[id]
          result[key] = quotient
          remainder -= quotient
        end

        if remainder > 0
          result['null'] = remainder
        end

        results[id] = {}
        result.sort_by(&:last).each do |key,value|
          results[id][key] = (value * 100).round(2)
        end
      end

      puts JSON.pretty_generate(results)
    end
  end
end
