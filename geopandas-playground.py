import geopandas as gpd
from datasets import api_hydrants_path, api_zones_path, api_structures_path, request_API_data

# Creates a 1-column geojson file containing fire hydrant coordinates
# from a json file collected from the Vermont Geoportal API
def hydrants_to_geojson(output_file_name, file_path):
    hydrant_path = file_path
    gdf = gpd.read_file(hydrant_path)
    # print(gdf.columns)

    # hydrant_data = gdf[["COUNTY", "HYDRANTID", "HYDRANTTYPE", "FLOWRATE", "geometry"]]
    hydrant_coords = gdf["geometry"]

    # print(hydrant_data)
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
    zone_polygons = gdf["geometry"]

    # print(zone_data)
    print(zone_polygons)

    print("Outputting %s.geojson..." % output_file_name)
    zone_polygons.to_file("%s.geojson" % output_file_name, driver="GeoJSON")


# Creates a 1-column geojson file containing fire station coordinates and related information
# from a json file collected from the Vermont Geoportal API
def stations_to_geojson(output_file_name, file_path):
    structure_data = file_path
    gdf = gpd.read_file(structure_data)
    
    # station_data = gdf[["COUNTY", "ESN", "ZIP", "ESZ", "geometry"]]
    station_coords = gdf["geometry"]

    # print(station_data)
    # print(station_coords)
    
    print("Outputting %s.geojson..." % output_file_name)
    station_coords.to_file("%s.geojson" % output_file_name, driver="GeoJSON")
    

if __name__ == "__main__":

    # Creates JSON files collected from the API to be ingested by GeoPandas
    request_API_data()

    # Filter through JSON data for geometry coordinates to be parsed in networkx
    # and store these as new geojson files whose name is the first argument to
    # the functions below (e.g., hydrant_coords.geojson).
    hydrants_to_geojson("hydrant_coords", api_hydrants_path)
    zones_to_geojson("zone_polygons", api_zones_path)
    stations_to_geojson("fire_station_coords", api_structures_path)

    