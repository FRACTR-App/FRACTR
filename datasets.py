import requests
import json

api_hydrants_path = "hydrants.json"
api_zones_path = "zones.json"
api_structures_path = "structures.json"

# Downloads data as JSON files from the Vermont Geoportal REST API
def request_API_data():
    # Make the request for E-911 hydrant data from VT Geoportal
    r = requests.get('https://opendata.arcgis.com/datasets/8429ff7bc1ba4abeb37d6c8ae49c8a8c_26.geojson')
    if not(r.raise_for_status()):
        # Create the json object
        hydrant_data = r.json()
        # Write the object to file.
        with open(api_hydrants_path,'w') as jsonFile:
            json.dump(hydrant_data, jsonFile)
    else:
        print("An error occurred while trying to retrieve hydrant data")


    # make the request for E-911 service zone data from VT Geoportal
    r = requests.get('https://opendata.arcgis.com/datasets/777ccbd85d8f4047906e37b0d16bf1e1_28.geojson')
    if not(r.raise_for_status()):
        # Create the json object
        zone_data = r.json()
        # Write the object to file.
        with open(api_zones_path,'w') as jsonFile:
            json.dump(zone_data, jsonFile)
    else:
        print("An error occurred while trying to retrieve service zone data")


    # make the request for E-911 structure data from VT Geoportal
    r = requests.get('https://opendata.arcgis.com/datasets/7a393abbbaa941449630361d9fd153c4_29.geojson')
    if not(r.raise_for_status()): 
        # Create the json object
        structures_data = r.json()
        # Write the object to file.
        with open(api_structures_path,'w') as jsonFile:
            json.dump(structures_data, jsonFile)
    else:
        print("An error occurred while trying to retrieve structure data")
