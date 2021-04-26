import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point, Polygon, shape
from tqdm import tqdm

ox.config(log_console=False, use_cache=True)

WEB_DIR = ""

# Returns a circular buffer (in meters) around a hydrant given the hydrant coordinates and the radius of the buffer
def make_buffer(hydrant, radius):
    # Create the buffer
    buffer = hydrant.buffer(radius)

    # Convert from Polygon to GeoSeries and undo projection
    buffer_series = gpd.GeoSeries(buffer, crs=3395)
    buffer_series = buffer_series.to_crs("EPSG:4326")

    # Convert from GeoSeries to GeoDataFrame
    buffer_gdf = gpd.GeoDataFrame([buffer_series])
    # Return the GeoSeries
    return buffer_gdf

########################################

if __name__ == "__main__":

    # Read in hydrant coordinate data
    hydrants = gpd.read_file("hydrant_coords.geojson")
    
    # Project the hydrant coordinates to Mercator
    hydrants = hydrants.to_crs(epsg=3395)

    # Initialize the dataframe that will hold all of the hydrant polygons
    hydrant_polys_gdf = gpd.GeoDataFrame()

    # Iterate through all of the hydants, creating the buffer polygons and add them to dataframe
    for i in tqdm(range(len(hydrants))):
        # Obtain the hydrant coordinates
        hydrant_of_interest = hydrants['geometry'].loc[i]
        # The buffer is initialized as 183 meters (600ft)
        buffer = make_buffer(hydrant_of_interest, 183)

        
        buffer.columns = ['geometry']
        hydrant_polys_gdf = hydrant_polys_gdf.append(buffer)
    
    # Make the dataframe into a geojson file
    hydrant_polys_gdf.to_file("%s.geojson" % (WEB_DIR + "hydrant_polys"), driver="GeoJSON")