from os import EX_SOFTWARE
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
    # Return the GeoDataFrame
    return buffer_gdf

########################################

if __name__ == "__main__":

    # Read in hydrant coordinate data
    hydrants = gpd.read_file("hydrant_coords.geojson")
    
    # Project the hydrant coordinates to Mercator
    hydrants = hydrants.to_crs(epsg=3395)

    # Initialize the dataframe that will hold all of the hydrant polygons
    hydrant_polys_gdf = gpd.GeoDataFrame()

    # Figure out the different hydrant flow rate categories
    for i in range(len(hydrants)):
        flow_rate = hydrants['FLOWRATE'].loc[i]
        if flow_rate is not None:
            edited_rate = flow_rate.split("g")[0]
            hydrants['FLOWRATE'].loc[i] = int(edited_rate)
        flow = hydrants['FLOWRATE'].loc[i]

    flow_rate_list = ['blue', 'green', 'orange', 'red', 'unknown']

    # List of dataframes for each flow rate
    gdf_list = []

    # Initialize as many GeoDataFrames as there are flow rate bins
    # Store these new GeoDataFrames in the gdf_list array.
    for i in range(len(flow_rate_list)):
        gdf_list.append(gpd.GeoDataFrame())

    # Iterate through all of the hydants, creating the buffer polygons and add them to dataframe
    for i in tqdm(range(len(hydrants))):
        # Obtain the hydrant coordinates
        hydrant_of_interest = hydrants['geometry'].loc[i]
        # Obtain the flowrate
        flow_rate = hydrants['FLOWRATE'].loc[i]
        # The buffer is initialized as 183 meters (600ft) - 305 meters = 1000ft
        buffer = make_buffer(hydrant_of_interest, 183)

        # Rename the geometry column
        buffer.columns = ['geometry']
        # Add a flowrate column to buffer dataframe
        buffer["FLOWRATE"] = flow_rate
        #buffer.assign(FLOWRATE = [flow_rate])
        #dfmi.loc[:, ('one', 'second')]
        
        hydrant_polys_gdf = hydrant_polys_gdf.append(buffer)
        print(hydrant_polys_gdf)
    
    # Filter through rows in hydrant_polys_gdf by flow_rate and append to corresponding GeoDataFrame()
    for j in range(len(flow_rate_list)):
            row = hydrant_polys_gdf.loc[
                (hydrant_polys_gdf['FLOWRATE'] == flow_rate_list[j]), 
                ['FLOWRATE', 'geometry']
            ]
            gdf_list[j] = gdf_list[j].append(row)

    # Convert each of the flow rate GeoDataFrames to geoJson files to be read by Leaflet
    for i in range(len(gdf_list)):
        flow = flow_rate_list[i]
        gdf_list[i].to_file("%s.geojson" % ("hydrant_" + str(flow)), driver="GeoJSON")
    
    # Make the dataframe into a geojson file
    #hydrant_polys_gdf.to_file("%s.geojson" % (WEB_DIR + "hydrant_polys"), driver="GeoJSON")