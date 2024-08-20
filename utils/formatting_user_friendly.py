'''
here i am converting the geojson returned from the initial function to a user friendly text, that gives information about
ETA, nearest distance, directions, etc.
'''

from fastapi import HTTPException
from utils.nearest_station_with_dir import find_nearest_station_with_directions

# processes nearest station and retuens formatted reponse
async def process_nearest_station(lat: float, lon: float, septa_kmz_file: str, dc_metro_stations: dict):
    nearest_station_info = await find_nearest_station_with_directions((lon, lat), septa_kmz_file, dc_metro_stations)
    
    if not nearest_station_info:
        raise HTTPException(status_code=404, detail="No nearest station found")

    station_name = nearest_station_info['properties']['name']
    distance_km = nearest_station_info['properties']['distance_km']
    walking_directions = nearest_station_info['properties']['walking_directions']['steps']
    total_walking_distance = nearest_station_info['properties']['walking_directions']['distance_km']
    total_duration = nearest_station_info['properties']['walking_directions']['duration_min']

    response_message = format_response_message(station_name, distance_km, walking_directions, total_walking_distance, total_duration)
    
    return response_message

# format information for readable messages with appropriate spacing
def format_response_message(station_name: str, distance_km: float, walking_directions: list, total_walking_distance: float, total_duration: float):
    """Format the information into a readable message with extra spacing."""
    response_message = (
        f"The nearest station to you is '{station_name}'.\n\n"
        f"It is approximately {distance_km:.2f} km away from your location.\n\n"
        "Walking directions:\n"
    )

    for index, step in enumerate(walking_directions):
        if step['duration_s'] == 0:
            response_message += f"And you have arrived at your destination.\n"
        else:
            response_message += (
                f"Step {index + 1}: Head {step['instruction'].lower()} for {step['distance_m'] / 1000:.2f} km, "
                f"which should take around {step['duration_s'] / 60:.2f} minutes.\n"
            )
    
    response_message += (
        f"\nThe total walking distance is {total_walking_distance:.2f} km.\n"
        f"It will take roughly {total_duration:.2f} minutes to reach your destination."
    )
    
    return response_message.strip()