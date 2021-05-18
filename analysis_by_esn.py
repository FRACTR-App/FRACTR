"""
Creating the response time networks
Based on code from https://towardsdatascience.com/how-to-calculate-travel-time-for-any-location-in-the-world-56ce639511f
and https://github.com/gboeing/osmnx-examples/blob/7cb65dbd64b5923a6013a94b72585f27d7a0acfa/notebooks/13-isolines-isochrones.ipynb
"""

import os
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
import alphashape
from tqdm import tqdm
from network_analysis import RESPONSE_TIMES

ox.config(log_console=False,
            use_cache=True,
            bidirectional_network_types=['drive_service'])

# Returns a response polygon (dataframe) that is bounded by its corresponding emergency service zone
def intersect_polygons(zone_polygon, response_polygon, agency_id, response_time):
    zone_series = gpd.GeoSeries(zone_polygon, crs=3395)
    zone_as_gdf = gpd.GeoDataFrame([zone_series])
    # Rename the geometry column appropriately
    zone_as_gdf.columns = ['geometry']

    response_series = gpd.GeoSeries(response_polygon, crs=3395)
    response_as_gdf = gpd.GeoDataFrame([response_series])
    # Rename the geometry column appropriately
    response_as_gdf.columns = ['geometry']
    
    # Perform the intersection
    join = gpd.overlay(response_as_gdf, zone_as_gdf, how="intersection")
    join.crs = "EPSG:3395"
    # Add the response time column
    join['response_time'] = response_time

    # Add the agency id column
    join['FIRE_AgencyId'] = agency_id
    
    # Return the dataframe containing the cookie-cutter response polygon
    join.to_crs(crs=3395)
    join.to_crs("EPSG:4326")
    return join


########################################

if __name__ == "__main__":

    # Read in the emergency service zones to be used for subgraphs  
    zone_polygons = gpd.read_file("data/zone_polygons.geojson")

    # Dissolve the ESN polygons into the wider FIRE_AgencyId zones
    zone_polygons = zone_polygons.dissolve(by = "FIRE_AgencyId").reset_index()

    # Output the ESN polygons to a geoJson, to be displayed on the website
    zone_polygons.to_file("data/dissolved_zones.geojson", driver = "GeoJSON")
    
    # initialize array to hold state-bounded-polygon geojson files
    response_polygons = []

    # Read in each of the response time geojson files 
    for time in RESPONSE_TIMES: # use the response time values in network_analysis.py
        response_time_gdf = gpd.read_file("data/%d.geojson" % (time / 60))
        response_polygons.append(response_time_gdf)
    
    # Initialize list that will hold the outputted dataframes with ESN polygons
    gdf_list = []

    # Initialize as many GeoDataFrames as there are response time bins
    # Store these new GeoDataFrames in the gdf_list array.
    for i in range(len(RESPONSE_TIMES)):
        gdf_list.append(gpd.GeoDataFrame())

    invalid_zone_polygons = []

    # Iterate over the response_geojson dataframes 
    for i in range(len(response_polygons)):
        response_dataframe = response_polygons[i]
        # Iterate over polygons in the dataframe
        # For each polygon, intersect it with its corresponding service zone based on Fire_AgencyId
        # Then add the new polygon to a new esn_based response time geojson

        for j in tqdm(range(len(response_dataframe))):
            response_polygon_geometry = response_dataframe['geometry'].loc[j]
            response_polygon_id = response_dataframe['FIRE_AgencyId'].loc[j]
            response_polygon_time = response_dataframe['response_time'].loc[j]
            # Locate the corresponding zone
            zone_coords = zone_polygons.loc[zone_polygons["FIRE_AgencyId"] == response_polygon_id, ["FIRE_AgencyId", "ESN", "geometry"]]
            #print(zone_coords)
            zone_poly = zone_coords["geometry"].iloc[0]

            # Double check that the zone polygon is valid
            if not(zone_poly.is_valid):
                invalid_zone_polygons.append(response_polygon_id)
                continue
            else:
                # Returns a GeoDataFrame with columns "response_time", "Agency Id" and "geometry"
                # where the geometry column contains the response time polygons
                bounded_response_poly = intersect_polygons(zone_poly, response_polygon_geometry, response_polygon_id, response_polygon_time)
                # Add the polygon dataframe to corresponding dataframe in gdf_list

                # Filter through rows in station_gdf by response_time and append to corresponding GeoDataFrame()
                for j in range(len(response_polygons)):
                    row = bounded_response_poly.loc[
                        (bounded_response_poly['response_time'] == RESPONSE_TIMES[j]), 
                        ['response_time', 'FIRE_AgencyId', 'geometry']
                    ]
                    gdf_list[j] = gdf_list[j].append(row)

    # Convert each of the response time GeoDataFrames to geoJson files to be read by Leaflet
    for i in range(len(gdf_list)):
        response_min = int(RESPONSE_TIMES[i]/60)
        gdf_list[i].to_file("data/%s_esn.geojson" % str(response_min), driver="GeoJSON")