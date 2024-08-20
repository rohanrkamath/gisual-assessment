import xml.etree.ElementTree as ET
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import PlainTextResponse
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from utils.dataset_extraction import load_geojson
from utils.get_walk_directions import *
from utils.lat_lon_check import lat_lon_check
from utils.formatting_user_friendly import *

from utils.cache.redis import *

from utils.security.rate_limit import check_rate_limit
from utils.security.api_key import validate_api_key

app = FastAPI()

# CORS Configuration - security feature 3, adding security headers and making sure unauthorised websites have no access amongst others
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # we can add the domain here that is to be trusted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTPS Redirection Middleware (if deploying with HTTP)
# app.add_middleware(HTTPSRedirectMiddleware)

# Trusted Host Middleware (restricting host headers to trusted domains)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*", "localhost"])

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to every response."""
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# this api handles both the septa and dc routes, and has the same structure 
# before the dc metro station data was integrated,  therefore is backwards compatible.
@app.get('/nearest_station', response_class=PlainTextResponse)
async def nearest_station(lat: float, lon: float, request: Request, api_key: APIKey = Depends(validate_api_key)):

    client_ip = request.client.host
    check_rate_limit(client_ip)

    location_key = f"{lat}_{lon}"

    lat_lon_check(lat, lon)

    cached_data = get_cached_data(location_key)
    if cached_data:
        return "Location already processed."

    if acquire_lock(location_key):
        try:
            dc_metro_stations = load_geojson('datasets/Metro_Stations_Regional.geojson')

            response_message = await process_nearest_station(lat, lon, 'datasets/SEPTARegionalRailStations2016.kmz', dc_metro_stations)
            cache_response(location_key, response_message)
            return PlainTextResponse(content=response_message)
        except Exception as e:
            logging.error(f"Error processing nearest station: {e}")
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
        finally:
            release_lock(location_key)
    else:
        raise HTTPException(status_code=429, detail="Request for this location is already being processed")

# should be removed before deployement, kept it for now.
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5001)