"""
Hydrant_analysis.py takes as input the hydrant_coords.geojson file,
sorts the hydrants based on flowrate (gallons per minute), 
and outputs the following geojson files:
- hydrant_unknown.geojson (hydrants with unknown flow rate)
- hydrant_red.geojson (less than 500 gpm)
- hydrant_orange.geojson (between 500 and 1000 gpm)
- hydrant_green.geojson (between 1000 and 1500 gpm)
- hydrant_blue.geojson (more than 1500 gpm)

These files contain geometric circles drawn around every hydrant. The circle radius
is 600 feet (183 meters), as this is the average maximum distance from which a fire engine 
can source water from the fire hydrant.

Authors: Halcyon Brown & John Cambefort
"""

import osmnx as ox
import geopandas as gpd
import pandas as pd
from tqdm import tqdm

ox.config(log_console=False, use_cache=True)

# Returns a circular buffer (in meters) around a hydrant given the hydrant coordinates 
# and the radius of the buffer
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

    # Read in the five hydrant coordinate datasets outputted by hydrant_coords_by_type.py
    file_paths = ["data/Dry_Hydrant_coords.geojson", "data/Drafting_Site_coords.geojson", 
            "data/Municipal_Hydrant_coords.geojson", "data/Pressurized_Hydrant_coords.geojson", 
            "data/Unknown_Type_coords.geojson"]
    # file_paths = ["Dry_Hydrant_coords.geojson", "Drafting_Site_coords.geojson", 
    #         "Municipal_Hydrant_coords.geojson", "Pressurized_Hydrant_coords.geojson", 
    #         "Unknown_Type_coords.geojson"]
    dataframesList = []
    for i in range(len(file_paths)):
        hydrant_file = gpd.read_file(file_paths[i])
        dataframesList.append(hydrant_file)
    hydrants = gpd.GeoDataFrame(pd.concat(dataframesList, ignore_index=True), crs=dataframesList[0].crs)

    hydrants = hydrants.head(50)
    # Read in hydrant coordinate data
    # hydrants = gpd.read_file("data/hydrant_coords.geojson")
    
    # Project the hydrant coordinates to Mercator
    hydrants = hydrants.to_crs(epsg=3395)

    # Initialize the dataframe that will hold all of the hydrant polygons
    hydrant_polys_gdf = gpd.GeoDataFrame()

    # Make a list containing the different hydrant colors based on flow rate (NFPA)
    flow_rate_list = ['blue', 'green', 'orange', 'red', 'unknown']

    # Make a list containing the different hydrant types 
    hydrant_type_list = ['Dry Hydrant', 'Drafting Site', 'Municipal Hydrant', 'Pressurized Hydrant', 'Unknown Type']

    # List of dataframes for each hydrant type
    gdf_list = []
 
    # Initialize as many GeoDataFrames as there are hydrant type bins
    # Store these new GeoDataFrames in the gdf_list array.
    for i in range(len(hydrant_type_list)):
        gdf_list.append(gpd.GeoDataFrame())

    # Iterate through all of the hydants, creating the buffer polygons and add them to dataframe
    for i in tqdm(range(len(hydrants))):
        # Obtain the hydrant coordinates
        hydrant_of_interest = hydrants['geometry'].loc[i]

        # Obtain the flowrate
        hydrant_color = hydrants['FLOWRATE'].loc[i]

        # Obtain the hydrant type
        hydrant_type = hydrants['HYDRANTTYPE'].loc[i]

        # Obtain the hydrant id
        hydrant_id = hydrants['HYDRANTID'].loc[i]

        # The buffer is initialized as 183 meters (600ft) - 305 meters = 1000ft
        buffer = make_buffer(hydrant_of_interest, 183)

        # Rename the geometry column
        buffer.columns = ['geometry']
        # Add a flowrate column to buffer dataframe
        buffer["FLOWRATE"] = hydrant_color
        # Add a hydrant type column to the buffer dataframe 
        buffer["HYDRANTTYPE"] = hydrant_type
        #print(buffer["HYDRANTTYPE"])
        #Add a hydrant id column to the buffer dataframe
        buffer["HYDRANTID"] = hydrant_id
        # Add the buffer to the dataframe for all hydrant buffers
        hydrant_polys_gdf = hydrant_polys_gdf.append(buffer)

    for j in range(len(hydrant_type_list)):
        row = hydrant_polys_gdf.loc[
            (hydrant_polys_gdf['HYDRANTTYPE'] == hydrant_type_list[j]), 
            ['HYDRANTID', 'FLOWRATE', 'HYDRANTTYPE', 'geometry']
        ]
        gdf_list[j] = gdf_list[j].append(row)

    # Convert each of the flow rate GeoDataFrames to geoJson files to be read by Leaflet
    for i in range(len(gdf_list)):
        hydrant_type = (hydrant_type_list[i]).replace(" ", "_")
        # Check to see if any dataframes are empty and if so, do not export them to geojson
        if (gdf_list[i]).empty:
            continue
        else:
            gdf_list[i].to_file("data/%s.geojson" % (str(hydrant_type) + "_buffers"), driver="GeoJSON")
            #gdf_list[i].to_file("%s.geojson" % (str(hydrant_type) + "_buffers"), driver="GeoJSON")