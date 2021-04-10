"""
BUILDING OFF CODE FROM network_analysis.py TO INCLUDE MULTIPLE STATIONS
Creating the response time networks
Based on code from https://towardsdatascience.com/how-to-calculate-travel-time-for-any-location-in-the-world-56ce639511f
and https://github.com/gboeing/osmnx-examples/blob/7cb65dbd64b5923a6013a94b72585f27d7a0acfa/notebooks/13-isolines-isochrones.ipynb
"""

from produce_geojson import stations_to_geojson
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
import matplotlib.pyplot as plt
from descartes import PolygonPatch
# from IPython.display import IFrame

ox.config(log_console=False, use_cache=True)

# Fetch "zone_polygons.geojson"
zones = gpd.read_file("zone_polygons.geojson") # Middlebury's zone polygon
stations = gpd.read_file("fire_station_coords.geojson") # Both Middlebury Fire Station
zone_geom = zones['geometry'].loc[0] # Get first element

# 1 - Create a graph
G = ox.graph_from_polygon(zone_geom, network_type='drive_service')
# G = ox.graph_from_point(station_tuple, dist=10000, dist_type='network', network_type='all')
# 2 - Create nodes geodataframe from Graph network (G)
gdf_nodes = ox.graph_to_gdfs(G, edges=False)

# Create a list of station geometries
station_nodes = []
for i in range(len(stations['geometry'])):
    station = stations['geometry'].loc[i]
    station_tuple = (station.y, station.x)
    station_of_interest = ox.get_nearest_node(G, point=station_tuple)
    station_nodes.append(station_of_interest)
    i+=1

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

fig, ax = ox.plot_graph(G, node_color=nc, node_size=ns, node_alpha=0.8, edge_linewidth=0.2,
    edge_color="#999999")


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
    isochrone_polys.append(bounding_poly)

# plot the network then add isochrones as colored descartes polygon patches
fig, ax = ox.plot_graph(G, show=False, close=False, edge_color='k', edge_alpha=0.2, node_color='none')
for polygon, fc in zip(isochrone_polys, iso_colors):
    patch = PolygonPatch(polygon, fc=fc, ec='none', alpha=0.6, zorder=-1)
    ax.add_patch(patch)
plt.show()

def make_iso_polys(G, edge_buff=25, node_buff=50, infill=False):
    isochrone_polys = []
    for response_time in sorted(response_times, reverse=True):
        subgraph = nx.ego_graph(G, station_of_interest, radius=response_time, distance='time')
        node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
        nodes_gdf = gpd.GeoDataFrame({"id": list(subgraph.nodes)}, geometry=node_points)
        nodes_gdf = nodes_gdf.set_index("id")

        edge_lines = []
        for n_fr, n_to in subgraph.edges():
            f = nodes_gdf.loc[n_fr].geometry
            t = nodes_gdf.loc[n_to].geometry
            edge_lookup = G.get_edge_data(n_fr, n_to)[0].get("geometry", LineString([f, t]))
            edge_lines.append(edge_lookup)

        n = nodes_gdf.buffer(node_buff).geometry
        e = gpd.GeoSeries(edge_lines).buffer(edge_buff).geometry
        all_gs = list(n) + list(e)
        new_iso = gpd.GeoSeries(all_gs).unary_union

        # try to fill in surrounded areas so shapes will appear solid and
        # blocks without white space inside them
        if infill:
            new_iso = Polygon(new_iso.exterior)
        isochrone_polys.append(new_iso)
    return isochrone_polys


isochrone_polys = make_iso_polys(G, edge_buff=25, node_buff=0, infill=True)
fig, ax = ox.plot_graph(
    G, show=False, close=False, edge_color="#999999", edge_alpha=0.2, node_size=0
)
for polygon, fc in zip(isochrone_polys, iso_colors):
    patch = PolygonPatch(polygon, fc=fc, ec="none", alpha=0.7, zorder=-1)
    ax.add_patch(patch)
plt.show()




def color_graph(G, response_times, station_tuple):

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
        # edge_color="#999999")

# plot the network then add isochrones as colored descartes polygon patches
# fig, ax = ox.plot_graph(G, show=False, close=False, edge_color='k', edge_alpha=0.2, node_color='none')
# for polygon, fc in zip(isochrone_polys, iso_colors):
#     patch = PolygonPatch(polygon, fc=fc, ec='none', alpha=0.6, zorder=-1)
#     ax.add_patch(patch)
# plt.show()

# def make_iso_polys(G, edge_buff=25, node_buff=50, infill=False):
#     isochrone_polys = []
#     for response_time in sorted(response_times, reverse=True):
#         subgraph = nx.ego_graph(G, station_of_interest, radius=response_time, distance='travel_time')
#         node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
#         nodes_gdf = gpd.GeoDataFrame({"id": list(subgraph.nodes)}, geometry=node_points)
#         nodes_gdf = nodes_gdf.set_index("id")

#         edge_lines = []
#         for n_fr, n_to in subgraph.edges():
#             f = nodes_gdf.loc[n_fr].geometry
#             t = nodes_gdf.loc[n_to].geometry
#             edge_lookup = G.get_edge_data(n_fr, n_to)[0].get("geometry", LineString([f, t]))
#             edge_lines.append(edge_lookup)

#         n = nodes_gdf.buffer(node_buff).geometry
#         e = gpd.GeoSeries(edge_lines).buffer(edge_buff).geometry
#         all_gs = list(n) + list(e)
#         new_iso = gpd.GeoSeries(all_gs).unary_union

#         # try to fill in surrounded areas so shapes will appear solid and
#         # blocks without white space inside them
#         if infill:
#             new_iso = Polygon(new_iso.exterior)
#         isochrone_polys.append(new_iso)
#     return isochrone_polys


# isochrone_polys = make_iso_polys(G, edge_buff=25, node_buff=0, infill=True)
# fig, ax = ox.plot_graph(
#     G, show=False, close=False, edge_color="#999999", edge_alpha=0.2, node_size=0
# )
# for polygon, fc in zip(isochrone_polys, iso_colors):
#     patch = PolygonPatch(polygon, fc=fc, ec="none", alpha=0.7, zorder=-1)
#     ax.add_patch(patch)
# plt.show()