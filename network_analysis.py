"""
Creating the response time networks 
Based on code from https://towardsdatascience.com/how-to-calculate-travel-time-for-any-location-in-the-world-56ce639511f

Need to figure out how to use edge times instead of a set speed (walking speed).
"""

from produce_geojson import stations_to_geojson
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
import matplotlib.pyplot as plt
from descartes import PolygonPatch
from pyproj import transform
# from IPython.display import IFrame

ox.config(log_console=False, use_cache=True)

# Fetch "zone_polygons.geojson"
zones = gpd.read_file("zone_polygons.geojson") # Middlebury's zone polygon
stations = gpd.read_file("fire_station_coords.geojson") # Both Middlebury Fire Station
zone_geom = zones['geometry'].loc[0] # Get first element
station_one_geom = stations['geometry'].loc[0]
print(type(zone_geom))
print(type(station_one_geom))
print(station_one_geom)

# transform the point geometry into a tuple (lat, long)
station_tuple = (station_one_geom.y, station_one_geom.x)
print(station_tuple)

# def create_graph(loc, distance, transport_mode, loc_type="points"):
#     # Transport mode = ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’, ‘none’
#     if loc_type == "address":
#         G = ox.graph_from_address(loc, dist=distance, dist_type="network", network_type=transport_mode)
#     elif loc_type == "points":
#         G = ox.graph_from_point(loc, dist=distance, dist_type="network", network_type=transport_mode)
#     return G

# 1 - Create a graph
G = ox.graph_from_polygon(zone_geom, network_type='drive_service')
# G = ox.graph_from_point(station_tuple, dist=10000, dist_type='network', network_type='all')
# 2 - Create nodes geodataframe from Graph network (G)
gdf_nodes = ox.graph_to_gdfs(G, edges=False)
# 3 - Specify where you want to start and get nearest nodes. 
station_of_interest = ox.get_nearest_node(G, point=station_tuple)

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

# For every edge, add a 'time' attribute in minutes.
# This is based on 'length' (originally in meters, converted here to km)
# and 'speed_kph' (added to the edge dict by add_edge_speeds(),
# and converted here to km/m).
# for _, _, _, data in G.edges(data=True, keys=True):
#     data["time"] = (data["length"] / 1000) / (data["speed_kph"] / 60) #km/m
#     print(data)

# 4 - Project a graph from lat-long to the UTM zone appropriate for its geographic location.
G = ox.project_graph(G)

# Response time in seconds
response_times = [120, 300]

# 1 - get one color for each isochrone
iso_colors = ox.plot.get_colors(n=len(response_times), cmap='Reds', start=0.3, return_hex=True)
# 2 - color the nodes according to isochrone then plot the street network
node_colors = {}

# Iterate over response times and possible colors
# Create subgraphs with nodes within radius (using time attributes of edges rather than a spatial distance)
# Associate nodes in the same subgraph to the same color
for trip_time, color in zip(sorted(response_times, reverse=True), iso_colors):
    subgraph = nx.ego_graph(G, station_of_interest, radius=trip_time, distance='travel_time')
    for node in subgraph.nodes():
        node_colors[node] = color

# Get list of possible node colors
nc = [node_colors[node] if node in node_colors else 'none' for node in G.nodes()]
# Get list of possible node sizes (i.e. whether or not we should display them)
ns = [20 if node in node_colors else 0 for node in G.nodes()]

# fig, ax = ox.plot_graph(G, node_color=nc, node_size=ns, node_alpha=0.8, edge_linewidth=0.2,
#     edge_color="#999999")


# make the isochrone polygons
i = 0
isochrone_polys = []
for response_time in sorted(response_times, reverse=True):
    subgraph = nx.ego_graph(G, station_of_interest, radius=response_time, distance='travel_time')
    node_points = [Point((data['lon'], data['lat'])) for node, data in subgraph.nodes(data=True)]

    bounding_poly = gpd.GeoSeries(node_points).unary_union.convex_hull
    poly_as_gdf = gpd.GeoSeries([bounding_poly])
    i += 1
    poly_as_gdf.to_file('poly{0}.geojson'.format(i), driver='GeoJSON')
    

# plot the network then add isochrones as colored descartes polygon patches
# fig, ax = ox.plot_graph(G, show=False, close=False, edge_color='k', edge_alpha=0.2, node_color='none')
# for polygon, fc in zip(isochrone_polys, iso_colors):
#     patch = PolygonPatch(polygon, fc=fc, ec='none', alpha=0.6, zorder=-1)
#     ax.add_patch(patch)
# plt.show()

"""
Questions for Joe:
- Nodes are currently road intersections, not buildings
- Convex vs concave hulls
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

"""

