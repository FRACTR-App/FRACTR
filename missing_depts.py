"""
Brainstorming how to locate missing departments and add them to the stations dataset.
"""

import os
import geopandas as gpd
from datasets import API_STRUCTURES_PATH, request_API_data

"""
List of not utilized departments:
BARRE CITY - 15 FOURTH ST - LAW ENFORCEMENT
Bellows Falls - 170 ROCKINGHAM ST - GOVERNMENT
FAIR HAVEN - 5 N PARK PL - TOWN OFFICE
HIGHGATE - 2996 VT ROUTE 78 - TOWN OFFICE
PLYMOUTH - 68 TOWN OFFICE RD - GOVERNMENT
SHEFFIELD-WHEELOCK - 37 DANE RD - TOWN OFFICE
STOCKBRIDGE - 1996 BLACKMER BLVD - TOWN GARAGE
STOWE - 350 S MAIN ST - LAW ENFORCEMENT
WINDSOR - 29 UNION ST - LAW ENFORCEMENT
RICHFORD - 48 MAIN ST - AMBULANCE SERVICE
ST. JOHNSBURY - 1187 MAIN ST - LAW ENFORCEMENT
SWANTON - 120 FIRST ST - LAW ENFORCEMENT
CRAFTSBURY - 46 TOWN GARAGE RD - TOWN GARAGE
WALDEN - 12 ROUTE 215 - GOVERNMENT


POWNAL VALLEY CENTRAL - 253 VT ROUTE 346 - FIRE STATION
ST. MICHAEL'S - 220 COLLEGE PKWY - FIRE STATION



"""

# Creates a 1-column geojson file containing fire station coordinates and related information
# from a json file collected from the Vermont Geoportal API
# Returns the GeoDataFrame (used to generate the output .geojson file)
def stations_to_geojson(output_file_name, input_file_path):
    structure_data = input_file_path
    gdf = gpd.read_file(structure_data)
    missing_station_coords = gpd.GeoDataFrame()

    missing_station_addresses = {"15 FOURTH ST": "LAW ENFORCEMENT", "170 ROCKINGHAM ST": "GOVERNMENT", "5 N PARK PL": "TOWN OFFICE", "2996 VT ROUTE 78": "TOWN OFFICE", "68 TOWN OFFICE RD": "GOVERNMENT",
        "37 DANE RD": "TOWN OFFICE", "1996 BLACKMER BLVD": "TOWN GARAGE", "350 S MAIN ST": "LAW ENFORCEMENT", "29 UNION ST": "LAW ENFORCEMENT", "48 MAIN ST": "AMBULANCE SERVICE", "1187 MAIN ST": "LAW ENFORCEMENT", 
        "120 FIRST ST": "LAW ENFORCEMENT", "46 TOWN GARAGE RD": "TOWN GARAGE", "12 ROUTE 215": "GOVERNMENT"}
    for key in missing_station_addresses:
        site_type = missing_station_addresses[key]
        missing_station_gdf = gdf.loc[(gdf["PRIMARYADDRESS"].str.contains(key)) & (gdf["SITETYPE"].str.contains(site_type)),
        ["PRIMARYADDRESS", "TOWNNAME", "ESN", "SITETYPE", "geometry"]]
        missing_station_coords = missing_station_coords.append(missing_station_gdf)

    # possible_station_coords = gdf.loc[gdf["PRIMARYADDRESS"].str.contains("2872 N POWNAL"),
    #     ["PRIMARYADDRESS", "TOWNNAME", "SITETYPE", "ESN", "geometry"]]
    # print(possible_station_coords)
    
    # possible_station_coords = gdf.loc[gdf["TOWNNAME"].str.contains("POWNAL"),
    #     ["PRIMARYADDRESS", "TOWNNAME", "SITETYPE", "ESN", "geometry"]]
    # print(possible_station_coords)


    # station_coords = gdf.loc[gdf["SITETYPE"].str.contains("FIRE STATION"),
    #     ["TOWNNAME", "ESN", "geometry"]]

    # print("Outputting %s.geojson..." % output_file_name)
    missing_station_coords.to_file("%s.geojson" % output_file_name, driver="GeoJSON")
    return missing_station_coords



########################################

# if __name__ == "__main__":

#     # Generate .json files collected from the GeoPortal API to be ingested by GeoPandas

#     # Create new .geojson files by filtering through JSON data for relevant columns
stations_to_geojson("missing_station_coords", "data/structures.json")
    