import geopandas as gpd
import osmnx as ox
from datasets import API_HYDRANTS_PATH, API_ZONES_PATH, API_STRUCTURES_PATH, request_API_data

# Middlebury ESN == 283

# Creates a 1-column geojson file containing fire hydrant coordinates
# from a json file collected from the Vermont Geoportal API
# Returns the GeoDataFrame (used to generate the output .geojson)
def hydrants_to_geojson(output_file_name, input_file_path):
    hydrant_path = input_file_path
    gdf = gpd.read_file(hydrant_path)
    # hydrant_data = gdf[["COUNTY", "HYDRANTID", "HYDRANTTYPE", "FLOWRATE", "geometry"]]

    hydrant_coords = gdf["geometry"]
    print(hydrant_coords)

    print("Outputting %s.geojson..." % output_file_name)
    hydrant_coords.to_file("%s.geojson" % output_file_name, driver="GeoJSON")

# Creates a 1-column geojson file containing only the emergency zone polygon coordinates
# from a json file collected from the Vermont Geoportal API
# Returns the GeoDataFrame (used to generate the output .geojson)
def zones_to_geojson(output_file_name, input_file_path):
    zone_path = input_file_path
    gdf = gpd.read_file(zone_path)
    # zone_data = gdf[["COUNTY", "FIRE", "ESZID", "FIRE_AgencyId", "ESN", "geometry"]]

    zone_polygons = gdf.loc[(gdf["ESN"] == 283),
        ["ESN", "geometry"]]

    print("Outputting %s.geojson..." % output_file_name)
    zone_polygons.to_file("%s.geojson" % output_file_name, driver="GeoJSON")

    return gdf


# Creates a 1-column geojson file containing fire station coordinates and related information
# from a json file collected from the Vermont Geoportal API
# Returns the GeoDataFrame (used to generate the output .geojson)
def stations_to_geojson(output_file_name, input_file_path):
    structure_data = input_file_path
    gdf = gpd.read_file(structure_data)
    
    station_coords = gdf.loc[gdf["SITETYPE"].str.contains("FIRE STATION") & (gdf["ESN"] == 283),
        ["ESN", "geometry"]]
    print(station_coords)
    
    print("Outputting %s.geojson..." % output_file_name)
    station_coords.to_file("%s.geojson" % output_file_name, driver="GeoJSON")
    return station_coords

# Creates a geojson file that includes the merged service zone and fire station index
# This does not merge both of the geometries, instead it keeps the zone geometry and the station index
def merged_to_geojson(output_file_name, file_path_1, file_path_2):
    zone_data = file_path_1
    station_data = file_path_2
    gdf_zone = gpd.read_file(zone_data)
    gdf_station = gpd.read_file(station_data)

    #merge the dataframes
    merged = gpd.sjoin(gdf_zone, gdf_station, how="inner", op="intersects")
    print(merged)
    
    print("Outputting %s.geojson..." % output_file_name)
    merged.to_file("%s.geojson" % output_file_name, driver="GeoJSON")
    return merged
    


if __name__ == "__main__":

    # Creates JSON files collected from the API to be ingested by GeoPandas
    # request_API_data()

    # Create new GEOJSON files by filtering through JSON data for relevant columns,
    # output geojson files
    
    # hydrants_to_geojson("hydrant_coords", API_HYDRANTS_PATH)
    zones_to_geojson("zone_polygons", API_ZONES_PATH)
    stations_to_geojson("fire_station_coords", API_STRUCTURES_PATH)
    # merged = merged_to_geojson("merged_zones_stations", 'zone_polygons.geojson', 'fire_station_coords.geojson')
    # print(merged)

    