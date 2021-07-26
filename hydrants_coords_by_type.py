"""
hydrant_coords_by_type.py generates the state fire hydrant datasets catagorized by hydrant type.

This module currently outputs the following files:
- Dry_Hydrant_coords.geojson (contains the dry hydrants)
- Drafting_Site_coords.geojson (contains the drafting sites)
- Municipal_Hydrant_coords.geojson (contains the municipal hydrants)
- Pressurized_Hydrant_coords.geojson (contains the pressurized hydrants)
- Unknown_Type_coords.geojson (contains the hydrants with unknown types)

It takes as input the hydrant_coords.geojson file that is created by produce_geojson.

These files are then used on the front end.

Authors: Halcyon Brown & John Cambefort
"""

import geopandas as gpd
from tqdm import tqdm

# Read in hydrant coordinate data
hydrants = gpd.read_file("data/hydrant_coords.geojson")
#hydrants = gpd.read_file("hydrant_coords_test.geojson")
#hydrants = hydrants.head(100)

# Figure out the different hydrant flow rate categories
for i in range(len(hydrants)):
    flow_rate = hydrants['FLOWRATE'].loc[i]
    if flow_rate is not None:
        edited_rate = flow_rate.split("g")[0]
        hydrants['FLOWRATE'].loc[i] = int(edited_rate)
    flow = hydrants['FLOWRATE'].loc[i]

# Make a list containing the different hydrant colors based on hydrant type
hydrant_type_list = ['Dry Hydrant', 'Drafting Site', 'Municipal Hydrant', 'Pressurized Hydrant', 'Unknown Type']

# List of dataframes for each hydrant_type
gdf_list = []

# Initialize dataframe to hold new hydrant entries
new_hydrant_gdf = gpd.GeoDataFrame()

# Initialize as many GeoDataFrames as there are hydrant_type bins
# Store these new GeoDataFrames in the gdf_list array.
for i in range(len(hydrant_type_list)):
    gdf_list.append(gpd.GeoDataFrame())

# Iterate through all of the hydants, determining hydrant color and type and add them to dataframe
for i in tqdm(range(len(hydrants))):
    # Obtain the hydrant coordinates
    hydrant_of_interest = hydrants['geometry'].loc[i]

    # Obtain the flowrate
    flow_rate = hydrants['FLOWRATE'].loc[i]

    # Obtain the hydrant type (coded as H1, H2, H3, H4)
    coded_type = hydrants['HYDRANTTYPE'].loc[i]
    #print(coded_type)

    # Figure out what hydrant color the flow_rate corresponds to
    hydrant_color = ""
    if (flow_rate == None):
        hydrant_color = 'unknown' 
    elif (int(flow_rate) >= 1500):
        hyrant_color = 'blue'
    elif (int(flow_rate) >= 1000 and int(flow_rate) < 1500):
        hydrant_color = 'green'
    elif (int(flow_rate) >= 500 and int(flow_rate) < 1000):
        hydrant_color = 'orange'
    elif (int(flow_rate) < 500):
        hydrant_color = 'red'
    else:
        hydrant_color = 'unknown'


    # Figure out what hydrant type the hydrant corresponds to based on HYDRANTTYPE
    hydrant_type = ""
    if (coded_type == "H1"):
        hydrant_type = "Municipal Hydrant"
    elif (coded_type == "H2"):
        hydrant_type = "Dry Hydrant"
    elif (coded_type == "H3"):
        hydrant_type = "Pressurized Hydrant"
    elif (coded_type == "H4"):
        hydrant_type = "Drafting Site"
    else:
        hydrant_type = "Unknown Type"

    # Add a flowrate column to hydrant dataframe
    #hydrant_of_interest["FLOWRATE"] = hydrant_color
    hydrants["FLOWRATE"].loc[i] = hydrant_color
    #print(hydrant_color)
    #print(hydrants["FLOWRATE"].loc[i])

    # Add a hydrant type column to the buffer dataframe 
    #hydrant_of_interest["HYDRANTTYPE"] = hydrant_type
    hydrants["HYDRANTTYPE"].loc[i] = hydrant_type
    #print(hydrants["HYDRANTTYPE"].loc[i])
    #print(hydrant_type)
    # Add the buffer to the dataframe for all hydrant buffers
    #new_hydrant_gdf = new_hydrant_gdf.append(hydrant_of_interest)

for j in range(len(hydrant_type_list)):
    row = hydrants.loc[
        (hydrants['HYDRANTTYPE'] == hydrant_type_list[j]), 
        ['HYDRANTID','FLOWRATE', 'HYDRANTTYPE', 'geometry']
    ]
    gdf_list[j] = gdf_list[j].append(row)

# Convert each of the hydrant type GeoDataFrames to geoJson files to be read by Leaflet
for i in range(len(gdf_list)):
    hyd_type = (hydrant_type_list[i]).replace(" ", "_")
    # Check to see if any dataframes are empty and if so, do not export them to geojson
    if (gdf_list[i]).empty:
        print("empty")
        print(hyd_type)
        continue
    else:
        print("outputting %s geojson file" % (hyd_type))
        #print(gdf_list[i])
        gdf_list[i].to_file("data/%s_coords.geojson" % (str(hyd_type)), driver="GeoJSON")
        #gdf_list[i].to_file("%s_coords.geojson" % (str(hyd_type)), driver="GeoJSON")