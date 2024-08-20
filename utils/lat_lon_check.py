''' a small check to make sure user inputs are correct '''

from fastapi import HTTPException

def lat_lon_check(lat, lon):
    if not (-90 <= lat <= 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90 degrees")
    if not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180 degrees")