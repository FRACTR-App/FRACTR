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

# Creates a 5-column geojson file containing fire hydrant coordinates, county, hydrant ID, 
# hydrant type and flow rate from a json file collected from the Vermont Geoportal API
# Returns the GeoDataFrame (used to generate the output .geojson file)
def hydrants_to_geojson(output_file_name, input_file_path):
    hydrant_path = input_file_path
    gdf = gpd.read_file(hydrant_path)
    hydrant_coords = gdf[["COUNTY", "HYDRANTID", "HYDRANTTYPE", "FLOWRATE", "geometry"]]

    print("Outputting %s.geojson..." % output_file_name)
    hydrant_coords.to_file("data/%s.geojson" % output_file_name, driver="GeoJSON")
    #hydrant_coords.to_file("%s_test.geojson" % output_file_name, driver="GeoJSON")
    return hydrant_coords


# Creates a 3-column geojson file containing the emergency service zone polygon coordinates 
# and ESN number and Fire Agency ID. These polygons include all zones, including police and emergency medical responder 
# zones. In analysis_by_esn.py, the Fire Department zones are extracted from this dataset
# and written to the esn_zones.py file.
# Returns the GeoDataFrame (used to generate the output .geojson file)
def zone_to_geojson(output_file_name, input_file_path):
    zone_path = input_file_path
    gdf = gpd.read_file(zone_path)
    zone_polygons = gdf[["ESN", "FIRE_AgencyId", "FIRE_DisplayName", "geometry"]]

    # If any FireAgency_Id value includes the substring "WEYBRIDGE", 
    # set the entire string to be simply "WEYBRIDGE".
    # This is to easily dissolve all different Weybridge ESNs into
    # one FIRE_AgencyId zone.
    zone_polygons.loc[zone_polygons["FIRE_AgencyId"].str.contains("WEYBRIDGE"),
        "FIRE_AgencyId"] = "WEYBRIDGE"
    zone_polygons.loc[zone_polygons["FIRE_DisplayName"].str.contains("WEYBRIDGE"),
        "FIRE_DisplayName"] = "WEYBRIDGE"

    print("Outputting %s.geojson..." % output_file_name)
    zone_polygons.to_file("data/%s.geojson" % output_file_name, driver="GeoJSON")
    #zone_polygons.to_file("%s_test.geojson" % output_file_name, driver="GeoJSON")

    return zone_polygons


# Creates a 3-column geojson file containing fire station coordinates, town name, and ESN
# from a json file collected from the Vermont Geoportal API
# Returns the GeoDataFrame (used to generate the output .geojson file)
def stations_to_geojson(output_file_name, input_file_path):
    structure_data = input_file_path
    gdf = gpd.read_file(structure_data)
    
    # Geodataframe that includes all structures with SITETYPE = FIRE STATION
    station_coords = gdf.loc[gdf["SITETYPE"].str.contains("FIRE STATION"),
        ["PRIMARYADDRESS", "TOWNNAME", "ESN", "SITETYPE", "geometry"]]
    
    # Geodataframe that includes all missing fire departments that have alternative SITETYPEs
    missing_station_coords = gpd.GeoDataFrame()

    missing_station_addresses = {"15 FOURTH ST": "LAW ENFORCEMENT", "170 ROCKINGHAM ST": "GOVERNMENT", "5 N PARK PL": "TOWN OFFICE", "2996 VT ROUTE 78": "TOWN OFFICE", "68 TOWN OFFICE RD": "GOVERNMENT",
        "37 DANE RD": "TOWN OFFICE", "1996 BLACKMER BLVD": "TOWN GARAGE", "350 S MAIN ST": "LAW ENFORCEMENT", "29 UNION ST": "LAW ENFORCEMENT", "48 MAIN ST": "AMBULANCE SERVICE", "1187 MAIN ST": "LAW ENFORCEMENT", 
        "120 FIRST ST": "LAW ENFORCEMENT", "46 TOWN GARAGE RD": "TOWN GARAGE", "12 ROUTE 215": "GOVERNMENT"}
    for key in missing_station_addresses:
        site_type = missing_station_addresses[key]
        missing_station_gdf = gdf.loc[(gdf["PRIMARYADDRESS"].str.contains(key)) & (gdf["SITETYPE"].str.contains(site_type)),
        ["PRIMARYADDRESS", "TOWNNAME", "ESN", "SITETYPE", "geometry"]]
        missing_station_coords = missing_station_coords.append(missing_station_gdf)

    # Append the two dataframes together ie. stations.append(missing)
    station_coords = station_coords.append(missing_station_coords)

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

# # Creates a 2-column geojson file containing surface water polygons
# # from a json file collected from the Vermont Geoportal API.
# # Returns the GeoDataFrame (used to generate the output .geojson file)
# def surface_water_to_geojson(output_file_name, input_file_path):
#     surface_water_data = input_file_path
#     gdf = gpd.read_file(surface_water_data)
#     surface_water_polygons = gdf[['FTYPE', 'geometry']]
    
#     print("Outputting %s.geojson..." % output_file_name)
#     surface_water_polygons.to_file("data/%s.geojson" % output_file_name, driver="GeoJSON")
#     return surface_water_polygons

# # Creates a 2-column geojson file containing surface water polygons
# # from a json file collected from the Vermont Geoportal API.
# # Returns the GeoDataFrame (used to generate the output .geojson file)
# def footprints_to_geojson(output_file_name, input_file_path):
#     footprints_data = input_file_path
#     gdf = gpd.read_file(footprints_data)
#     footprint_polygons = gdf[['FOOTPRINTTYPE', 'NAME', 'PRIMARYADDRESS', 'TOWNNAME', 'geometry']]
    
#     print("Outputting %s.geojson..." % output_file_name)
#     footprint_polygons.to_file("data/%s.geojson" % output_file_name, driver="GeoJSON")
#     return footprint_polygons

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
    # surface_water_to_geojson("surface_water_polygons", API_SURFACE_WATER_PATH)
    # footprints_to_geojson("footprint_polygons", API_FOOTPRINTS_PATH)