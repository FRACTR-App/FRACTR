"""
Datasets.py attempts to ping the Vermont Open Geodata Portal API once,
to download the E911 Fire Hydrants, E911 Emergency Service Zones,
E911 Site Structures (which includes fire stations) and Vermont State geometry
datasets as .json files.  Each of these datasets includes a geometry column.

These files are ingested by produce_geojson.py which parses and filters the data 
to preserve only required information (e.g. Fire Department info).

Authors: Halcyon Brown & John Cambefort
"""

import os
import requests
import json

API_HYDRANTS_PATH = "data/hydrants.json"
API_ZONES_PATH = "data/zones.json"
API_STRUCTURES_PATH = "data/structures.json"
API_VERMONT_PATH = "data/vermont.json"

# Downloads data as JSON files from the Vermont Geoportal REST API
def request_API_data():

    # Make the request for E-911 hydrant data from VT Geoportal
    r = requests.get('https://opendata.arcgis.com/datasets/faa4109d4a504dcfbe3b6af6f752fbb7_0.geojson')
    if not(r.raise_for_status()):
        # Create the json object
        hydrant_data = r.json()
        # Write the object to file.
        with open(API_HYDRANTS_PATH,'w') as jsonFile:
            json.dump(hydrant_data, jsonFile)
    else:
        print("An error occurred while trying to retrieve hydrant data")
        exit(1) # Exit to warn maintainers of an error related to the API

    # make the request for E-911 service zone data from VT Geoportal
    r = requests.get('https://opendata.arcgis.com/datasets/2fcd8223c02b450f8ef12218c4bb1917_0.geojson')
    if not(r.raise_for_status()):
        # Create the json object
        zone_data = r.json()
        # Write the object to file.
        with open(API_ZONES_PATH,'w') as jsonFile:
            json.dump(zone_data, jsonFile)
    else:
        print("An error occurred while trying to retrieve service zone data")
        exit(1) # Exit to warn maintainers of an error related to the API

    # make the request for E-911 structure data from VT Geoportal
    r = requests.get('https://opendata.arcgis.com/datasets/b226846d719a4b3fa59485a41aed1ddf_0.geojson')
    if not(r.raise_for_status()): 
        # Create the json object
        structures_data = r.json()
        # Write the object to file.
        with open(API_STRUCTURES_PATH,'w') as jsonFile:
            json.dump(structures_data, jsonFile)
    else:
        print("An error occurred while trying to retrieve structure data")
        exit(1) # Exit to warn maintainers of an error related to the API

    # make the request for state of Vermont polygon from VT Geoportal
    r = requests.get('https://opendata.arcgis.com/datasets/ad7e257457364c71a050f9291eafc806_31.geojson')
    if not(r.raise_for_status()): 
        # Create the json object
        vermont_state_data = r.json()
        # Write the object to file.
        with open(API_VERMONT_PATH,'w') as jsonFile:
            json.dump(vermont_state_data, jsonFile)
    else:
        print("An error occurred while trying to retrieve Vermont state data")
        exit(1) # Exit to warn maintainers of an error related to the API
