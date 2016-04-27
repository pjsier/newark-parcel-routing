import numpy as np
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame, GeoSeries
import pysal

# Load initial csv file
routing = pd.read_csv('/var/otp/scripting/output/otp-scripting-newark-parcels.csv')
routing["min_time"] = routing["min_time"].astype(float)

# Split out by mode of transportation
transit_routing = routing[routing["mode"] == "TRANSIT,WALK"]
walk_routing = routing[routing["mode"] == "WALK"]
car_routing = routing[routing["mode"] == "CAR"]

# Get distance and time pivots for each mode
transit_time_pivot = transit_routing.pivot(index="ID", columns="school", values="min_time")
transit_distance_pivot = transit_routing.pivot(index="ID", columns="school", values="route_distance")

walk_time_pivot = walk_routing.pivot(index="ID", columns="school", values="min_time")
walk_distance_pivot = walk_routing.pivot(index="ID", columns="school", values="route_distance")

car_time_pivot = car_routing.pivot(index="ID", columns="school", values="min_time")
car_distance_pivot = car_routing.pivot(index="ID", columns="school", values="route_distance")

# Reset indices so that dataframes work on merge
pivots = [transit_time_pivot, transit_distance_pivot, walk_time_pivot, walk_distance_pivot,
          car_time_pivot, car_distance_pivot]

for p in pivots:
    p.reset_index(inplace=True)

# Write each pivot to csv
transit_time_pivot.to_csv("output/pivot-csv/transit-time-pivot.csv")
transit_distance_pivot.to_csv("output/pivot-csv/transit-distance-pivot.csv")
walk_time_pivot.to_csv("output/pivot-csv/walk-time-pivot.csv")
walk_distance_pivot.to_csv("output/pivot-csv/walk-distance-pivot.csv")
car_time_pivot.to_csv("output/pivot-csv/car-time-pivot.csv")
car_distance_pivot.to_csv("output/pivot-csv/car-distance-pivot.csv")

# Get shapefile into GeoDataFrame
newark_blocks = GeoDataFrame.from_file("data/newark-residential-parcels/newark-residential-parcels-4326.shp")
newark_blocks["ID"] = newark_blocks["ID"].astype(int)

# Merge into new dataframes
transit_time_merge = pd.merge(newark_blocks, transit_time_pivot, on="ID")
transit_distance_merge = pd.merge(newark_blocks, transit_distance_pivot, on="ID")
walk_time_merge = pd.merge(newark_blocks, walk_time_pivot, on="ID")
walk_distance_merge = pd.merge(newark_blocks, walk_distance_pivot, on="ID")
car_time_merge = pd.merge(newark_blocks, car_time_pivot, on="ID")
car_distance_merge = pd.merge(newark_blocks, car_distance_pivot, on="ID")

merges = [transit_time_merge, transit_distance_merge, walk_time_merge, walk_distance_merge,
          car_time_merge, car_distance_merge]

# Set CRS to use for all
crs = {'init': 'epsg:4326', 'no_defs': True}

for m in merges:
    # Set each geometry column to GeoSeries
    # Documented bug: https://github.com/geopandas/geopandas/issues/247)
    m.geometry = m.geometry.astype(gpd.geoseries.GeoSeries)
    m.geometry.crs = crs
    m["ID"] = m["ID"].astype(str)
    # Convert column names to strings (so that fiona doesn't throw error)
    m.rename(columns = lambda x: str(x), inplace=True)

# Convert DataFrames back to GeoDataFrames (bug in geopandas)
transit_time_merge = GeoDataFrame(transit_time_merge, crs=crs, geometry=transit_time_merge.geometry)
transit_distance_merge = GeoDataFrame(transit_distance_merge, crs=crs, geometry=transit_distance_merge.geometry)
walk_time_merge = GeoDataFrame(walk_time_merge, crs=crs, geometry=walk_time_merge.geometry)
walk_distance_merge = GeoDataFrame(walk_distance_merge, crs=crs, geometry=walk_distance_merge.geometry)
car_time_merge = GeoDataFrame(car_time_merge, crs=crs, geometry=car_time_merge.geometry)
car_distance_merge = GeoDataFrame(car_distance_merge, crs=crs, geometry=car_distance_merge.geometry)

# Write to shapefiles
transit_time_merge.to_file("output/merged-shp/transit-time.shp")
transit_distance_merge.to_file("output/merged-shp/transit-distance.shp")
walk_time_merge.to_file("output/merged-shp/walk-time.shp")
walk_distance_merge.to_file("output/merged-shp/walk-distance.shp")
car_time_merge.to_file("output/merged-shp/car-time.shp")
car_distance_merge.to_file("output/merged-shp/car-distance.shp")
