import geopandas as gpd
from datasets import API_HYDRANTS_PATH, API_ZONES_PATH, API_STRUCTURES_PATH, API_VERMONT_PATH, request_API_data

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

# Creates a 2-column geojson file containing the emergency zone polygon coordinates and ESN number
# from a json file collected from the Vermont Geoportal API
# Returns the GeoDataFrame (used to generate the output .geojson)
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

    # Merge polygons with the same FIRE_AgencyId (i.e. of the same FD ESN)
    # clean_zone = zone_polygons.dissolve(by = "FIRE_AgencyId")

    print("Outputting %s.geojson..." % output_file_name)
    zone_polygons.to_file("%s.geojson" % output_file_name, driver="GeoJSON")

    return gdf


# Creates a 1-column geojson file containing fire station coordinates and related information
# from a json file collected from the Vermont Geoportal API
# Returns the GeoDataFrame (used to generate the output .geojson)
def stations_to_geojson(output_file_name, input_file_path):
    structure_data = input_file_path
    gdf = gpd.read_file(structure_data)
    
    station_coords = gdf.loc[gdf["SITETYPE"].str.contains("FIRE STATION"),
        ["TOWNNAME", "FIRE_AgencyId", "ESN", "geometry"]]

    # Testing purposes
    # station_coords = gdf.loc[gdf["SITETYPE"].str.contains("FIRE STATION") & (gdf["ESN"] == 283),
        # ["ESN", "geometry"]]
    # station_coords = gdf.loc[gdf["ESN"] == 283,
        # ["ESN", "geometry"]]

    print("Outputting %s.geojson..." % output_file_name)
    station_coords.to_file("%s.geojson" % output_file_name, driver="GeoJSON")
    return station_coords


# Creates a 1-column geojson file containing Vermont state polygon
# from a json file collected from OpenDataSoft API
# Returns the GeoDataFrame (used to generate the output .geojson)
def vermont_to_geojson(output_file_name, input_file_path):
    vermont_data = input_file_path
    gdf = gpd.read_file(vermont_data)
    vermont_coords = gdf['geometry']
    
    print("Outputting %s.geojson..." % output_file_name)
    vermont_coords.to_file("%s.geojson" % output_file_name, driver="GeoJSON")
    return vermont_coords


########################################

if __name__ == "__main__":

    # Generate JSON files collected from the GeoPortal API to be ingested by GeoPandas
    # request_API_data()

    # Create new GEOJSON files by filtering through JSON data for relevant columns,
    # output geojson files
    # stations_to_geojson("fire_station_coords", API_STRUCTURES_PATH)
    # vermont_to_geojson("vermont_state_polygon", API_VERMONT_PATH)
    zone_to_geojson("zone_polygons", API_ZONES_PATH)
    
    