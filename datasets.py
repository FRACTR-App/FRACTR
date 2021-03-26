import requests
import json
#make the request for E-911 hydrant data from VT Geoportal
r = requests.get('https://opendata.arcgis.com/datasets/8429ff7bc1ba4abeb37d6c8ae49c8a8c_26.geojson')
if r.raise_for_status():
    #Create the json object
    hydrant_data = r.json()
    #Write the object to file.
    with open('hydrants.json','w') as jsonFile:
        json.dump(hydrant_data, jsonFile)
else:
    print("An error occurred while trying to retrieve hydrant data")

