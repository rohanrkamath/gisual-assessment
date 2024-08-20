import math
import aiohttp  # Use aiohttp for asynchronous HTTP requests
import logging
from fastapi import HTTPException
import json

''' this function calculates the initial bearing between two points on the earth (specified in decimal degrees) 
and returns it as a compass bearing (in degrees). the result is a value between 0 and 360, where 0 corresponds to North, 
90 to East, 180 to South, and 270 to West. '''
async def calculate_initial_compass_bearing(pointA, pointB):
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])
    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)
    compass_bearing = (math.degrees(initial_bearing) + 360) % 360

    return compass_bearing

# this function maps a compass bearing to one of the eight cardinal directions (North, NorthEast, East, SouthEast, South, SouthWest, West, NorthWest).
def get_cardinal_direction(bearing):
    directions = ['North', 'NorthEast', 'East', 'SouthEast', 'South', 'SouthWest', 'West', 'NorthWest']
    idx = round(bearing / 45) % 8
    return directions[idx]

# this function fetches walking directions from the OSRM API and calculates detailed steps with cardinal directions.
async def get_walking_directions(origin, destination):
    url = f"http://router.project-osrm.org/route/v1/walking/{origin[1]},{origin[0]};{destination[1]},{destination[0]}?overview=false&steps=true"
    
    logging.info(f"Fetching walking directions from {origin} to {destination}")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                raw_response = await response.text()
                logging.info(f"OSRM API raw response: {raw_response}")
                
                try:
                    data = json.loads(raw_response)
                    logging.info(f"OSRM API parsed response: {data}")

                    if not data['routes'] or not data['routes'][0]['legs']:
                        logging.error("No routes or legs found in the OSRM response")
                        raise HTTPException(status_code=500, detail="No walking directions found")

                    distance = data['routes'][0]['distance'] / 1000  
                    duration = data['routes'][0]['duration'] / 60  

                    steps = []
                    last_point = origin
                    for leg in data['routes'][0]['legs']:
                        for step in leg['steps']:
                            current_point = (step['maneuver']['location'][1], step['maneuver']['location'][0])  # (lat, lon)
                            bearing = await calculate_initial_compass_bearing(last_point, current_point)
                            direction = get_cardinal_direction(bearing)
                            instruction = f"Head {direction}"
                            steps.append({
                                "distance_m": step['distance'],  # distance in meters
                                "duration_s": step['duration'],  # duration in seconds
                                "instruction": instruction  # text
                            })
                            last_point = current_point

                    return {
                        "distance_km": distance,
                        "duration_min": duration,
                        "steps": steps
                    }
                except Exception as e:
                    logging.error(f"Failed to parse OSRM API response: {e}")
                    raise HTTPException(status_code=500, detail="Error fetching walking directions")
            else:
                logging.error(f"OSRM API request failed with status code {response.status}")
                raise HTTPException(status_code=response.status, detail="Failed to fetch walking directions")
