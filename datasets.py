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
# API_SURFACE_WATER_PATH = "data/surface_water.json"
# API_FOOTPRINTS_PATH = "data/footprints.json"

# Downloads data as JSON files from the Vermont Geoportal REST API
def request_API_data():

    # Make the request for E-911 hydrant data from VT Geoportal
    r = requests.get('https://opendata.arcgis.com/datasets/8429ff7bc1ba4abeb37d6c8ae49c8a8c_26.geojson')
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
    r = requests.get('https://opendata.arcgis.com/datasets/777ccbd85d8f4047906e37b0d16bf1e1_28.geojson')
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
    r = requests.get('https://opendata.arcgis.com/datasets/7a393abbbaa941449630361d9fd153c4_29.geojson')
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
    
    # # make the request for VT Hydrography Dataset - Cartographic Extract Polygons from VT Geoportal
    # r = requests.get('https://opendata.arcgis.com/datasets/87b11946959a4961a0f594208ae7ccd3_11.geojson')
    # if not(r.raise_for_status()): 
    #     # Create the json object
    #     surface_water_data = r.json()
    #     # Write the object to file.
    #     with open(API_SURFACE_WATER_PATH,'w') as jsonFile:
    #         json.dump(surface_water_data, jsonFile)
    # else:
    #     print("An error occurred while trying to retrieve surface water data")
    #     exit(1) # Exit to warn maintainers of an error related to the API
    
    # # make the request for E-911 Footprints Dataset from VT Geoportal
    # r = requests.get('https://opendata.arcgis.com/datasets/8112dd2b554745c981aea87a9a1bc69e_27.geojson')
    # if not(r.raise_for_status()): 
    #     # Create the json object
    #     footprints_data = r.json()
    #     # Write the object to file.
    #     with open(API_FOOTPRINTS_PATH,'w') as jsonFile:
    #         json.dump(footprints_data, jsonFile)
    # else:
    #     print("An error occurred while trying to retrieve footprints data")
    #     exit(1) # Exit to warn maintainers of an error related to the API
