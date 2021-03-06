"""
Creating the response time networks based on Emergency Service Zones
Based on code from https://towardsdatascience.com/how-to-calculate-travel-time-for-any-location-in-the-world-56ce639511f
and https://github.com/gboeing/osmnx-examples/blob/7cb65dbd64b5923a6013a94b72585f27d7a0acfa/notebooks/13-isolines-isochrones.ipynb
"""

import os
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point, Polygon, shape
import alphashape
from tqdm import tqdm
import pandas

ox.config(log_console=False,
            use_cache=True,
            bidirectional_network_types=['drive_service'])

# Returns a Graph of edges & nodes within the bounding_zone polygon geometry
def make_graph(bounding_zone):

    # Create a graph based on a drive_service (all roads including service roads) road network
    G = ox.graph_from_polygon(bounding_zone, network_type='drive_service')

    # Project the graph from lat-long to the UTM zone appropriate for its geographic location.
    G = ox.project_graph(G)

    # Pass in default speed values (km/hour) to fill in edges from Open Street Maps
    # with missing `maxspeed` values
    hwy_speeds = {"residential": 40, 
                "unclassified": 40,
                "tertiary": 56, 
                "secondary": 56, 
                "primary": 80, 
                "trunk": 56
                }
    # # 25 mph, 35 mph, 50 mph

    G = ox.add_edge_speeds(G, hwy_speeds)
    G = ox.add_edge_travel_times(G)

    return G


# Returns a GeoDataFrame containing polygon geometries and a response time column
def compute_subgraphs(G, response_times, station):
    
    # initialize the geodataframe
    station_polygons = gpd.GeoDataFrame()
    
    # Fetch the station's nearest node
    station_tuple = (station.y, station.x)
    station_node = ox.get_nearest_node(G, point=station_tuple, method='euclidean')

    # Iterate over response times bins for that station
    for i in range(len(response_times)):
        response_time = response_times[i]

        # Create the subgraph for the station and the response time
        subgraph = nx.ego_graph(G, station_node, radius=response_time, distance='travel_time')

        node_points_coords = [Point((data['lon'], data['lat'])) for node, data in subgraph.nodes(data=True)]

        # bounding_poly_coords = gpd.GeoSeries(node_points_coords).unary_union.convex_hull

        # Make list of nodes into GeoSeries multi-point
        multi_point = gpd.GeoSeries(node_points_coords).unary_union
        # Create a concave hull polygon from the multi-point
        concave_hull = alphashape.alphashape(multi_point, 30)
        # Convert back to a GeoSeries then to a GeoDataFrame
        bounding_poly_coords = gpd.GeoSeries(concave_hull)
        poly_as_gdf = gpd.GeoDataFrame([bounding_poly_coords])
        
        # Rename the geometry column appropriately
        poly_as_gdf.columns = ['geometry']
        
        # Add the response time column
        poly_as_gdf['response_time'] = response_time
        
        # Append the polygon for that station to our GeoDataFrame
        station_polygons = station_polygons.append(poly_as_gdf)

    # Return the GeoDataFrame containing polygon bins for the station
    return station_polygons


########################################

if __name__ == "__main__":
    
    # Read in station coordinate data
    stations = gpd.read_file("fire_station_coords.geojson")
    
    # Read in the bounding zone to be used for the wide Vermont graph
    bounding_zone = gpd.read_file("vermont_state_polygon.geojson")["geometry"].loc[0]

    # Read in the emergency service zones to be used for subgraphs
    zone_polygons = gpd.read_file("zone_polygons.geojson")

    print("Making Vermont graph...")

    # Store the Vermont graph in a .graphml file so we don't need to recompute
    # it every time from the geoJson
    if not os.path.exists("vermont_graph.graphml"):
        G = make_graph(bounding_zone)
        ox.save_graphml(G, "vermont_graph.graphml")
    else:
        G = ox.load_graphml("vermont_graph.graphml")

    print("Graph made!")
    
    # Project the station nodes to the same CRS as that of the Graph
    stations = ox.projection.project_gdf(stations, to_crs=G.graph['crs'], to_latlong=False)

    # Response time in seconds
    response_times = [120, 300, 600, 1200]

    # List of dataframes for each response time
    gdf_list = []

    #List of station ESNs where the station's EMZ is not valid
    poly_not_valid = []


    # We need to use the FIRE_AgencyId zones as the bounding zones for station response times.
    # The zone_polygons.geojson polygons are currently for every ESN.
    # To achieve this:
    # 1. We create a "FIRE_AgencyId" column in the stations dataset
    # 2. We retrieve this value for every station based on the unique ESNs in the zones dataset
    #    and the ESN that we have for the station
    # 3. We dissolve the ESN polygons into the wider Fire agency ID zones
    # 4. And we finally use these Fire Agency ID polygons as bounding zones for the stations,
    #    in computing our travel times.

    # Step 1: create a "FIRE_AgencyId" column in the stations dataset
    stations["FIRE_AgencyId"] = ""

    # Step 2: For every station (and its ESN), fetch the ESN's FIRE_AgencyId from zones
    for i in range(len(stations)):
        station_esn = stations["ESN"].loc[i]
        station_agency_id = zone_polygons.loc[station_esn == zone_polygons["ESN"], ["FIRE_AgencyId"]].values[0][0]
        stations.loc[stations.index[i], "FIRE_AgencyId"] = station_agency_id

    # Write this information back to file as it may be used later
    # stations.to_file("agencyid_fire_station_coords.geojson", driver = "GeoJSON")
    print(stations)

    # Step 3: dissolve the ESN polygons into the wider FIRE_AgencyId zones
    zone_polygons = zone_polygons.dissolve(by = "FIRE_AgencyId").reset_index()
    # zone_polygons.to_file("dissolved_zones.geojson", driver = "GeoJSON")

    # Initialize as many GeoDataFrames as there are response time bins (typically 2 to 4).
    # Store these new GeoDataFrames in the gdf_list array.
    for i in range(len(response_times)):
        gdf_list.append(gpd.GeoDataFrame())

    # Iterate over every station
    for i in tqdm(range(len(stations))):
        try:
            # Select the station Point object to be passed as a param to compute_subgraphs()
            station_of_interest = stations['geometry'].loc[i]
            print(station_of_interest)

            # Step 4: use the FIRE_AgencyId polygons as bounding zones.
            # Create the graph for the station's corresponding Fire Dept. zone using the FIRE_AgencyId
            station_fd_zone = stations['FIRE_AgencyId'].loc[i]
            zone_coords = zone_polygons.loc[zone_polygons["FIRE_AgencyId"] == station_fd_zone, ["FIRE_AgencyId", "ESN", "geometry"]]
            print(zone_coords)
            zone_poly = zone_coords["geometry"].iloc[0]
        
            # Create the graph for the emergency service zone if the polygon is valid
            if not(zone_poly.is_valid):
                poly_not_valid.append(station_fd_zone)
                continue
            else:
                esn_graph = make_graph(zone_poly)

                # Returns a GeoDataFrame with columns "response_time" and "geometry"
                # where the geometry column contains the response time polygons
                station_gdf = compute_subgraphs(esn_graph, response_times, station_of_interest)

                # Filter through rows in station_gdf by response_time and append to corresponding GeoDataFrame()
                for j in range(len(response_times)):
                    row = station_gdf.loc[
                        (station_gdf['response_time'] == response_times[j]), 
                        ['response_time', 'geometry']
                    ]
                    gdf_list[j] = gdf_list[j].append(row)
        
        except TypeError as e:
            print(e)
    
    # Print a list of ESN for which their emergency response polygon was considered invalid
    # and network analysis for that station was therefore not conducted
    print(poly_not_valid)
    # Convert each of the response time GeoDataFrames to geoJson files to be read by Leaflet
    for i in range(len(gdf_list)):
        response_min = int(response_times[i]/60)
        gdf_list[i].to_file("%s_esn.geojson" % str(response_min), driver="GeoJSON")