"""
Produce_geojson.py takes as input the raw .json data files fetched from the Vermont
Open Geodata Portal API by datasets.py
It filters and parses this data to preserve only relevant information.
The following .geojson files are then output:
- hydrant_coords.geojson
- fire_station_coords.geojson
- vermont_state_polygon.geojson
- zone_polygons.geojson (contains general state emergency service zones; 
  Fire Dept. zones are later created in analysis_by_esn.py and zone_polygons.geojson
  does not represent the Fire Dept. zones yet)

These files are then ingested into the network_analysis.py file to compute response times
from every fire station. The fire hydrants are processed in hydrant_analysis.py.

All data files are written to the data folder of the project Website directory and
may be downloaded from there: https://github.com/This-blank-Is-On-Fire/Website

Authors: Halcyon Brown & John Cambefort
"""

import os
import geopandas as gpd
from datasets import API_HYDRANTS_PATH, API_ZONES_PATH, API_STRUCTURES_PATH, API_VERMONT_PATH, request_API_data

# Creates a 1-column geojson file containing fire hydrant coordinates
# from a json file collected from the Vermont Geoportal API
# Returns the GeoDataFrame (used to generate the output .geojson file)
def hydrants_to_geojson(output_file_name, input_file_path):
    hydrant_path = input_file_path
    gdf = gpd.read_file(hydrant_path)
    hydrant_coords = gdf[["COUNTY", "HYDRANTID", "HYDRANTTYPE", "FLOWRATE", "geometry"]]

    print("Outputting %s.geojson..." % output_file_name)
    hydrant_coords.to_file("data/%s.geojson" % output_file_name, driver="GeoJSON")

# Creates a 2-column geojson file containing the emergency service zone polygon coordinates 
# and ESN number. These polygons include all zones, including police and emergency medical responder 
# zones. In analysis_by_esn.py, the Fire Department zones are extracted from this dataset
# and written to the esn_zones.py file.
# Returns the GeoDataFrame (used to generate the output .geojson file)
def zone_to_geojson(output_file_name, input_file_path):
    zone_path = input_file_path
    gdf = gpd.read_file(zone_path)
    zone_polygons = gdf[["ESN", "FIRE_AgencyId", "geometry"]]

    # If any FireAgency_Id value includes the substring "WEYBRIDGE", 
    # set the entire string to be simply "WEYBRIDGE".
    # This is to easily dissolve all different Weybridge ESNs into
    # one FIRE_AgencyId zone.
    zone_polygons.loc[zone_polygons["FIRE_AgencyId"].str.contains("WEYBRIDGE"),
        "FIRE_AgencyId"] = "WEYBRIDGE"

    print("Outputting %s.geojson..." % output_file_name)
    zone_polygons.to_file("data/%s.geojson" % output_file_name, driver="GeoJSON")

    return gdf


# Creates a 1-column geojson file containing fire station coordinates and related information
# from a json file collected from the Vermont Geoportal API
# Returns the GeoDataFrame (used to generate the output .geojson file)
def stations_to_geojson(output_file_name, input_file_path):
    structure_data = input_file_path
    gdf = gpd.read_file(structure_data)
    
    station_coords = gdf.loc[gdf["SITETYPE"].str.contains("FIRE STATION"),
        ["TOWNNAME", "ESN", "geometry"]]

    print("Outputting %s.geojson..." % output_file_name)
    station_coords.to_file("data/%s.geojson" % output_file_name, driver="GeoJSON")
    return station_coords


# Creates a 1-column geojson file containing Vermont state polygon
# from a json file collected from OpenDataSoft API
# Returns the GeoDataFrame (used to generate the output .geojson file)
def vermont_to_geojson(output_file_name, input_file_path):
    vermont_data = input_file_path
    gdf = gpd.read_file(vermont_data)
    vermont_coords = gdf['geometry']
    
    print("Outputting %s.geojson..." % output_file_name)
    vermont_coords.to_file("data/%s.geojson" % output_file_name, driver="GeoJSON")
    return vermont_coords


########################################

if __name__ == "__main__":

    # Make sure the data folder exists (where all json / geojsons are output)
    if not os.path.exists('data'):
        os.makedirs('data')

    # Generate .json files collected from the GeoPortal API to be ingested by GeoPandas
    request_API_data()

    # Create new .geojson files by filtering through JSON data for relevant columns
    stations_to_geojson("fire_station_coords", API_STRUCTURES_PATH)
    vermont_to_geojson("vermont_state_polygon", API_VERMONT_PATH)
    zone_to_geojson("zone_polygons", API_ZONES_PATH)
    hydrants_to_geojson("hydrant_coords", API_HYDRANTS_PATH)
    