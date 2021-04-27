"""
This is a dump file that is used for brainstorming

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
from tqdm import tqdm
import alphashape
# from IPython.display import IFrame

ox.config(log_console=False, use_cache=True)

# Fetch "zone_polygons.geojson"
zones = gpd.read_file("midd_zone.geojson") # Middlebury's zone polygon
stations = gpd.read_file("midd_station.geojson") # Both Middlebury Fire Station
#zone_geom = zones['geometry'].loc[0] # Get first element
station = stations['geometry'].loc[0]
print(station)
esn = stations['ESN'].loc[0]
print(type(esn))
print(esn)
#zone = zones.loc[zones['ESN'] == esn, ['geometry']]
#print(zone)
#zone_coords = zones['geometry'].loc[0]
#print(zone_geom)
zone_coords = zones.loc[zones["ESN"] == esn,
         ["geometry"]]
zone_final = zone_coords['geometry'].loc[0]
#print(zone_final)
# zone_final = ox.projection.project_gdf(zone_final, to_crs=G.graph['crs'], to_latlong=False)
# print(zone_final)
# print(zone_coords)
# Project the station nodes to the same CRS as that of the Graph
    #stations = ox.projection.project_gdf(stations, to_crs=G.graph['crs'], to_latlong=False)

#print(zone_poly)
        #polygon_gs = gpd.GeoSeries(zone_poly, crs='epsg:4326')
        # Project the station nodes to the same CRS as that of the Graph
        #zone_proj = ox.projection.project_gdf(polygon_gs, to_crs=G.graph['crs'], to_latlong=False)
        #print(zone_proj)
        # Convert geoseries to geodataframe
        #zone_gdf = gpd.GeoDataFrame(polygon_gs)
        #zone_final = zone_gdf["geometry"].loc[0]
        #print(zone_final)
# 1 - Create a graph
G = ox.graph_from_polygon(zone_final, network_type='drive_service')
# G = ox.graph_from_point(station_tuple, dist=10000, dist_type='network', network_type='all')
# 2 - Create nodes geodataframe from Graph network (G)
gdf_nodes = ox.graph_to_gdfs(G, edges=False)


station_tuple = (station.y, station.x)
station = ox.get_nearest_node(G, point=station_tuple)

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
    subgraph = nx.ego_graph(G, station, radius=trip_time, distance='travel_time')
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
    subgraph = nx.ego_graph(G, station, radius=response_time, distance='travel_time')
    node_points = [Point((data['lon'], data['lat'])) for node, data in subgraph.nodes(data=True)]
    #node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
    #bounding_poly = gpd.GeoSeries(node_points).unary_union.convex_hull
    poly_as_gdf = gpd.GeoSeries(node_points)
    concave_hull = alphashape.alphashape(poly_as_gdf, alpha = 0.2)
    isochrone_polys.append(concave_hull)

# plot the network then add isochrones as colored descartes polygon patches
fig, ax = ox.plot_graph(G, show=False, close=False, edge_color='k', edge_alpha=0.2, node_color='none')
for polygon, fc in zip(isochrone_polys, iso_colors):
    patch = PolygonPatch(polygon, fc=fc, ec='none', alpha=0.6, zorder=-1)
    ax.add_patch(patch)
plt.show()





# def make_iso_polys(G, edge_buff=25, node_buff=50, infill=False):
#     isochrone_polys = []
#     for response_time in sorted(response_times, reverse=True):
#         subgraph = nx.ego_graph(G, station, radius=response_time, distance='time')
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




# def color_graph(G, response_times, station_tuple):

#     # 1 - get one color for each isochrone
#     iso_colors = ox.plot.get_colors(n=len(response_times), cmap='Reds', start=0.3, return_hex=True)
#     # 2 - color the nodes according to isochrone then plot the street network
#     node_colors = {}

#     # Iterate over response times and possible colors
#     # Create subgraphs with nodes within radius (using time attributes of edges rather than a spatial distance)
#     # Associate nodes in the same subgraph to the same color
#     for trip_time, color in zip(sorted(response_times, reverse=True), iso_colors):
#         subgraph = nx.ego_graph(G, station_of_interest, radius=trip_time, distance='travel_time')
#         for node in subgraph.nodes():
#             node_colors[node] = color

#     # Get list of possible node colors
#     nc = [node_colors[node] if node in node_colors else 'none' for node in G.nodes()]
#     # Get list of possible node sizes (i.e. whether or not we should display them)
#     ns = [20 if node in node_colors else 0 for node in G.nodes()]

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