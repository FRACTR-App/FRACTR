"""
This file takes in fire_station_coords.geojson and department_types.json. It outputs a new geojson file 
that contains all the information from fire_station_coords.geojson with the addition of the department type column.
"""

import pandas as pd
import geopandas as gpd
from tqdm import tqdm
import re

#files needed: 
# department_types.json
# fire_station_coords.geojson

# We are going to merge these two datasets using the town name and fire department 
# 1. Add a Dept Type property to fire_station_coords.geojson
# 2. Truncate the department name to only include the town name 
# 3. Find a match
# 4. Update Dept Type property to include the department type for the matched station

# Read in department type data
dept_types = pd.read_json("department_types.json")

# Read in station coordinate data
stations = gpd.read_file("fire_station_coords_test.geojson")

# Read in the emergency service zones to be used for subgraphs
zone_polygons = gpd.read_file("zone_polygons_test.geojson")

# We need to add a Fire_AgencyId column to the fire stations dataset so that 
# our response time geojson files can also contain this column.
# Step 1: create an empty "FIRE_AgencyId" column in the stations dataset
stations["Department_Type"] = ""
stations["Department_Name"] = ""
dept_types["Department_Name"] = ""
dept_types["Utilized"] = "No"
unmatched_list = []

# We can use the json key as the department name
# Need to figure out how to access json elements using the key - not the same as geodataframe??
for i in range(len(dept_types)):
    department = dept_types.iloc[i]
    #print(department)
    department_name = department["Dept Name"]
    #print(department_name)
    #department_name = department_name.split(" Fire")[0].upper()
    department_name = re.split(" Fire| Volunteer| FD", department_name)[0].upper()
    #print(department_name)
    dept_types.loc[dept_types.index[i], "Department_Name"] = department_name

for i in tqdm(range(len(stations))):
    station_esn = stations["ESN"].loc[i]
    #print(station_esn)
    station_name = zone_polygons.loc[station_esn == zone_polygons["ESN"], ["FIRE_DisplayName"]].values[0][0]
    #print(station_name)
    #station_name = station_name.split(" F")[0].upper()
    station_name = re.split(" FD| FIRE| VFD| VOL| HOSE| EMERGENCY", station_name)[0].upper()
    #print(station_name)
    stations.loc[stations.index[i], "Department_Name"] = station_name

    # Need to capture error when a station does not match with a department
    station_dept = dept_types.loc[(dept_types["Department_Name"] == station_name)]
    #print(station_dept)
    if (station_dept.empty):
        unmatched_list.append(station_name)
        print("Error: unmatched station " + station_name)
    else:
        dept_types.loc[(dept_types["Department_Name"] == station_name), "Utilized"] = "Yes"
        station_type = station_dept.iloc[0]["Type Description"]
        #print(station_type)
        stations.loc[stations.index[i], "Department_Type"] = station_type

stations.to_file("updated_stations_coords.geojson", driver="GeoJSON")
print("list of unmatched stations: ")
print(unmatched_list)
#print(dept_types)

# Keep track of the fire departments that were never merged from dept_types
# These are missing departments on our maps that may be labeled as law enforcement (site type)
not_utilized_departments = []
for i in range(len(dept_types)):
    department = dept_types.iloc[i]
    if (department["Utilized"] == "No"):
        department_name = department["Department_Name"]
        not_utilized_departments.append(department_name)
print("List of not utilized departments:")
print(not_utilized_departments)
