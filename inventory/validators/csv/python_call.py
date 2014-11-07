import sys
import json
from Naked.toolshed.shell import muterun_rb

response = muterun_rb('validate_csv.rb', 'http://donnees.ville.montreal.qc.ca/dataset/84a5beb4-4223-43b0-b8c8-48e32ec366a0/resource/c69b0dd2-55e6-476f-8805-085375b85d38/download/donneesqualo2013.csv')

if response.exitcode == 0:
  json_content = response.stdout.decode("utf-8")
  data = json.loads(json_content)

  if data["valid"] == False:
    print ("CSV not valid - list of errors:")
    for error in data["errors"]:
      print (error)
  else:
    print ("CSV is valid")

else:
  sys.stderr.write(response.stderr)

