"""
Creating the response time networks
Based on code from https://towardsdatascience.com/how-to-calculate-travel-time-for-any-location-in-the-world-56ce639511f
and https://github.com/gboeing/osmnx-examples/blob/7cb65dbd64b5923a6013a94b72585f27d7a0acfa/notebooks/13-isolines-isochrones.ipynb
"""

import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point

ox.config(log_console=False, use_cache=True)  

# Returns a Graph of edges & nodes within the bounding_zone polygon geometry
def make_graph(bounding_zone):

    # 1 - Create a graph
    G = ox.graph_from_polygon(bounding_zone, network_type='drive_service')
    # G = ox.graph_from_point(station_tuple, dist=10000, dist_type='network', network_type='all')
    # 2 - Create nodes geodataframe from Graph network (G)
    gdf_nodes = ox.graph_to_gdfs(G, edges=False)

    # Pass in a few default speed values (km/hour)
    # to fill in edges with missing `maxspeed` from OSM
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

    # 4 - Project a graph from lat-long to the UTM zone appropriate for its geographic location.
    G = ox.project_graph(G)

    return G


# Returns a GeoDataFrame containing polygon geometries and a response time column
def compute_subgraphs(G, stations, response_time):
    
    # initialize the geodataframe
    polygons = gpd.GeoDataFrame()

    for i in range(len(stations)):
        # Fetch a station coordinates
        station = stations['geometry'].loc[i]
        station_tuple = (station.y, station.x)

        print(station_tuple)

        # Fetch the station's nearest node
        station_node = ox.get_nearest_node(G, point=station_tuple)
        print(station_node)

        # Create the subgraph for the station and the response time
        subgraph = nx.ego_graph(G, station_node, radius=response_time, distance='travel_time')
        # using lat, long to make polygons
        node_points_coords = [Point((data['lon'], data['lat'])) for node, data in subgraph.nodes(data=True)]

        bounding_poly_coords = gpd.GeoSeries(node_points_coords).unary_union.convex_hull
        poly_as_gdf = gpd.GeoDataFrame([bounding_poly_coords])
        
        # Rename the geometry column appropriately
        poly_as_gdf.columns = ['geometry']
        
        # Add the response time column
        poly_as_gdf['response_time'] = response_time
        
        # Append the polygon for that station to our polygons GeoDataFrame
        polygons = polygons.append(poly_as_gdf)

    # Return the polygons geodataframe
    # print(polygons)
    return polygons


########################################

if __name__ == "__main__":
    
    # Read in data
    zones = gpd.read_file("midd_zone.geojson")
    stations = gpd.read_file("midd_station.geojson")
    
    bounding_zone = zones['geometry'].loc[0] # Get first zone element
    #bounding_zone = gpd.read_file("vermont_state_polygon.geojson")["geometry"].loc[0]

    G = make_graph(bounding_zone)
    # fig, ax = ox.plot_graph(G)

    # Response time in seconds
    response_times = [120, 300]
    geo_names = ["poly2", "poly5"]

    # for i in range(len(stations['geometry'])): # iterate over every station
    for i in range(len(response_times)): # and over every response time

        # Returns a GeoDataFrame with columns "response_time" and "geometry"
        # where the geometry column contains the polygons for the
        # response time bin passed as an input
        response_gdf = compute_subgraphs(G, stations, response_times[i])
        
        # Convert the gdf to geojson
        response_gdf.to_file("{0}.geojson".format(geo_names[i]), driver="GeoJSON")

########################################
########################################

"""
Questions for Joe:
- Nodes are currently road intersections, not buildings
- Convex vs concave hulls vs buffers
- How to handle overlap?
- Best way to 'export' the polygons together (into a layer?)?
  Export as one vector layer of multiple polygons? Raster heat map? (rasters are pixel-based,
  vectors are point-based / have nodes, edges and polygons) What would be easier for Leaflet to
  show / compute browser-side? Leaflet can take in geojson files, and other data formats?
- ESNs / overlap of stations: e.g. it takes North Midd 5 mins and East Midd 10 mins to reach a node.
  Which bin should the node be placed?
  - If we want to have the shortest response time on top: how can we prevent Leaflet
    from adding up the fillColors of the different features?
- When a user zooms in or out, should they see different layers? E.g. if zoomed out,
  see only a binary of reachable and non-reachable zones in one bin (maybe 20 minutes).
  If zoomed in, see all of the bins for a given area.
- Polygons vs buffer zones for display
- 3 Different geojson files, where every file contains polygon features of the same bin
- Follow-up: how can one create toggleable layers? Is this possible from geojson files?
  Do all features (here: polygons) from the same geojson file considered to be in the
  same LayerGroup?

Try to use a concave hull (geopandas)
Tesselation of hexagons
One base VT network: subgraphs that change an edge attributes for the bins,
to handle overlap
Tile vectorization if we want to map roads / many vector features
 (not needed if polygons / areas are used as they're less computationally expensive
 for a browser)
Visualizing edges / roads rather than polygons, maybe


"""