import json

jsonfile = open('SatData.json')
data = json.load(jsonfile)
print(data['SatelliteName'])
