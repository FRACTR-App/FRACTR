#Playing around with OSMnx and Networkx

import osmnx as ox
import networkx as nx

#Easily get access to different locations (these can be points or polygons)
place1 = ox.geocode_to_gdf('Vermnont, USA')
place2 = ox.geocode_to_gdf('Addison County, Vermnont, USA')
place3 = ox.geocode_to_gdf('Middlebury, Vermnont, USA')

"""
Specify type of street network:
'drive'
'drive_service'
'walk'
'bike'
'all'
'all_private'
"""

#Get street network from bounding box
G = ox.graph_from_bbox(37.79, 37.78, -122.41, -122.43, network_type='drive')
G_projected = ox.project_graph(G)
ox.plot_graph(G_projected)

#Get street network from point
G = ox.graph_from_point((37.79, -122.41), dist=750, network_type='all')
ox.plot_graph(G)
#You can input a certain network to the "street network from point or address" in order to 
# find nodes within a certain distance of an address that are in the bounds of the inputted network
# network from address, including only nodes within 1km along the network from the address
G = ox.graph_from_address(
    address="350 5th Ave, New York, NY",
    dist=1000,
    dist_type="network",
    network_type="drive",
)
# you can project the network to UTM (zone calculated automatically)
G_projected = ox.project_graph(G)

#Get street network from polygon using Geopandas
G = ox.graph_from_polygon(shapefile, network_type='drive')
ox.plot_graph(G)


#PS. you can convert your graph to node and edge GeoPandas GeoDataFrames
"""
Saving files

OSMnx can save the street network to disk as a GraphML file to work with 
later in Gephi or networkx. Or it can save the network (such as this one, 
for the New York urbanized area) as ESRI shapefiles or GeoPackages to work 
with in any GIS
"""
# save graph to shapefile, geopackage, or graphml
ox.save_graph_shapefile(G, filepath="./graph_shapefile/")
ox.save_graph_geopackage(G, filepath="./graph.gpkg")
ox.save_graphml(G, filepath="./graph.graphml")

"""
I think we will want to do the following for response time network:
1) import our fire station points
2) import our service zones
3) create and save street networks (we want this to be roads, service roads, and private roads?)
    for each of the service zones
4) figure out which fire stations lie within each service zone 
5) create a graph from a point (fire station) where the inputted network is the service zone network
    how do we deal with multiple stations in each service zone?
    we might have to iterate over each of the fire stations, creating a graph for each and stitching them together
"""

"""
I think we will want to do the following for hydrant network:
1) import our hydrant points
2) create and save street networks (we want this to be roads, service roads, and private roads?)
    for each of the service zones - we do this just to make the calculations easier
3) figure out which hydrants lie within each service zone 
4) create a graph from a point (hydrant) where the inputted network is the service zone network
    and the distance is xxxx (the distance I get from chief)
"""
#for hydrants, we could create polygons xx distance around a hydrant and perform the network analysis within those polygons and stitch together
# ex. osmnx.utils_geo.bbox_from_point(point, dist=1000, project_utm=False, return_crs=False)

"""
GOOD REFERENCES
https://automating-gis-processes.github.io/2017/lessons/L7/network-analysis.html
https://github.com/gboeing/osmnx-examples/tree/7cb65dbd64b5923a6013a94b72585f27d7a0acfa/notebooks
https://networkx.org/documentation/latest/auto_examples/geospatial/plot_osmnx.html
https://networkx.org/documentation/latest/auto_examples/geospatial/plot_delaunay.html 
    *how to use multiple coordinates from a geometry column by putting them into an array using numpy
https://networkx.org/documentation/latest/auto_examples/geospatial/plot_osmnx.html
https://osmnx.readthedocs.io/en/stable/osmnx.html#module-osmnx.stats
"""
#THE ISSUES: how do we create a graph from multiple starting points (multiple stations in 
# a service zone or many hydrants in the same area)???