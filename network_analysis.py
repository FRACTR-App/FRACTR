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
from IPython.display import IFrame

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

def create_graph(loc, dist, transport_mode, loc_type="points"):
    # Transport mode = ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’, ‘none’
    if loc_type == "address":
        G = ox.graph_from_address(loc, distance=dist, dist_type="network", network_type=transport_mode)
    elif loc_type == "points":
        G = ox.graph_from_point(loc, distance=dist, dist_type="network", network_type=transport_mode)
    return G

# 1 - Create a graph
G = ox.graph_from_point(station_tuple, dist=20000, dist_type='network', network_type='drive_service')
# 2 - Create nodes geodataframe from Graph network (G)
gdf_nodes = ox.graph_to_gdfs(G, edges=False)
# 3 - Specify where you want to start and get nearest nodes. 
station_of_interest = ox.get_nearest_node(G, point=station_tuple)

# Pass in a few default speed values (km/hour)
# to fill in edges with missing `maxspeed` from OSM
hwy_speeds = {"residential": 40, "secondary": 56, "tertiary": 80}
   
G = ox.add_edge_speeds(G, hwy_speeds)
G = ox.add_edge_travel_times(G)



# 4 - Project a graph from lat-long to the UTM zone appropriate for its geographic location.
G = ox.project_graph(G)

# Response time in mintues
response_times = [0.5, 1, 1.5, 2, 3, 5]
for i in range(len(response_times)):
   response_times[i] = response_times[i] * 60
print(response_times)

# 1 - get one color for each isochrone
iso_colors = ox.plot.get_colors(n=len(response_times), cmap='Reds', start=0.3, return_hex=True)
# 2 - color the nodes according to isochrone then plot the street network
node_colors = {}
for trip_time, color in zip(sorted(response_times, reverse=True), iso_colors):
    subgraph = nx.ego_graph(G, station_of_interest, radius=trip_time, distance='time')
    for node in subgraph.nodes():
        node_colors[node] = color
nc = [node_colors[node] if node in node_colors else 'none' for node in G.nodes()]
ns = [20 if node in node_colors else 0 for node in G.nodes()]
fig, ax = ox.plot_graph(G, node_color=nc, node_size=ns, node_alpha=0.8, edge_linewidth=0.2,
    edge_color="#999999",)


# # make the isochrone polygons
# isochrone_polys = []
# for trip_time in sorted(response_times, reverse=True):
#     subgraph = nx.ego_graph(G, station_of_interest, radius=trip_time, distance='time')
#     node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
#     bounding_poly = gpd.GeoSeries(node_points).unary_union.convex_hull
#     isochrone_polys.append(bounding_poly)

# # plot the network then add isochrones as colored descartes polygon patches
# fig, ax = ox.plot_graph(G, show=False, close=False, edge_color='k', edge_alpha=0.2, node_color='none')
# for polygon, fc in zip(isochrone_polys, iso_colors):
#     patch = PolygonPatch(polygon, fc=fc, ec='none', alpha=0.6, zorder=-1)
#     ax.add_patch(patch)
# plt.show()



