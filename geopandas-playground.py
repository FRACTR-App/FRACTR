import geopandas

# Gets hydrant coordinates from a .json and stores them in a .geoJson file
data_path = "/Users/john/Documents/College/Courses/CS/CS701/FireDeserts/hydrants.json"
gdf = geopandas.read_file(data_path)
hydrant_coords = gdf["geometry"]
print(hydrant_coords)
hydrant_coords.to_file("hydrant_coords.geojson", driver="GeoJSON")