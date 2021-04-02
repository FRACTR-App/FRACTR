import geopandas as gpd
from datasets import api_hydrants_path, api_zones_path, api_structures_path, request_API_data

# Creates a 1-column geojson file containing fire hydrant coordinates
# from a json file collected from the Vermont Geoportal API
def hydrants_to_geojson(output_file_name, file_path):
    hydrant_path = file_path
    gdf = gpd.read_file(hydrant_path)
    # print(gdf.columns)

    # hydrant_data = gdf[["COUNTY", "HYDRANTID", "HYDRANTTYPE", "FLOWRATE", "geometry"]]
    # print(hydrant_data)

    hydrant_coords = gdf["geometry"]
    print(hydrant_coords)

    print("Outputting %s.geojson..." % output_file_name)
    hydrant_coords.to_file("%s.geojson" % output_file_name, driver="GeoJSON")

# Creates a 1-column geojson file containing only the emergency zone polygon coordinates
# from a json file collected from the Vermont Geoportal API
def zones_to_geojson(output_file_name, file_path):
    zone_path = file_path
    gdf = gpd.read_file(zone_path)
    # print(gdf.columns)

    # zone_data = gdf[["COUNTY", "ESZID", "FIRE_AgencyId", "ESN", "geometry"]]
    # print(zone_data)

    zone_polygons = gdf[["ESN", "geometry"]]
    print(zone_polygons)

    print("Outputting %s.geojson..." % output_file_name)
    zone_polygons.to_file("%s.geojson" % output_file_name, driver="GeoJSON")

    return zone_polygons


# Creates a 1-column geojson file containing fire station coordinates and related information
# from a json file collected from the Vermont Geoportal API
def stations_to_geojson(output_file_name, file_path):
    structure_data = file_path
    gdf = gpd.read_file(structure_data)
    
    station_coords = gdf.loc[gdf["SITETYPE"].str.contains("FIRE STATION"), ["ESN", "geometry"]]
    print(station_coords)
    # print(gdf.SITETYPE.unique())
    
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

    # Filter through JSON data for geometry coordinates to be parsed in networkx
    # and store these as new geojson files whose name is the first argument to
    # the functions below (e.g., hydrant_coords.geojson).
    # hydrants_to_geojson("hydrant_coords", api_hydrants_path)
    
    zones_to_geojson("zone_polygons", api_zones_path)
    stations_to_geojson("fire_station_coords", api_structures_path)
    merged = merged_to_geojson("merged_zones_stations", 'zone_polygons.geojson', 'fire_station_coords.geojson')
    print(merged)

    