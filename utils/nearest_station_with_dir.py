'''
this function is the first task in the docs. it returns a geojson, and the properties have the walking directions to the 
station (bonus).
'''

from json import load
from utils.dataset_extraction import parse_kmz, load_geojson
from utils.haversine_distance import haversine
from utils.get_walk_directions import get_walking_directions

import logging

async def find_nearest_station_with_directions(location, septa_kmz_file, dc_geojson):
    user_lon, user_lat = location
    
    logging.info(f"Finding nearest station to location: {location}")

    # Extract KML data from KMZ for SEPTA
    septa_kml_data = parse_kmz(septa_kmz_file)
    dc_metro_data = dc_geojson['features']
    
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    min_distance = float('inf')
    nearest_station = None
    walking_directions = None
    
    # Search in SEPTA dataset
    for placemark in septa_kml_data.findall('.//kml:Placemark', namespace):
        name = placemark.find('.//kml:name', namespace).text
        coordinates = placemark.find('.//kml:coordinates', namespace).text.strip()
        lon, lat, _ = map(float, coordinates.split(','))

        distance = haversine(user_lon, user_lat, lon, lat)
        
        if distance < min_distance:
            min_distance = distance
            nearest_station = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "name": name,
                    "distance_km": distance
                }
            }
            walking_directions = await get_walking_directions((user_lat, user_lon), (lat, lon))

    # Search in DC Metro dataset
    for station in dc_metro_data:
        name = station['properties']['NAME']
        lon, lat = station['geometry']['coordinates']

        distance = haversine(user_lon, user_lat, lon, lat)
        
        if distance < min_distance:
            min_distance = distance
            nearest_station = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "name": name,
                    "distance_km": distance
                }
            }
            walking_directions = await get_walking_directions((user_lat, user_lon), (lat, lon))
    
    if nearest_station and walking_directions:
        nearest_station['properties']['walking_directions'] = walking_directions
    
    logging.info(f"Nearest station: {nearest_station}")
    
    return nearest_station
