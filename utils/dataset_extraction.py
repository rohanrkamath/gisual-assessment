'''
this file is just to parse and load teh data.
'''

import zipfile
import xml.etree.ElementTree as ET
import json
import logging
from fastapi import HTTPException

def parse_kmz(kmz_file):
    with zipfile.ZipFile(kmz_file, 'r') as z:
        for filename in z.namelist():
            if filename.endswith('.kml'):
                with z.open(filename) as kml_file:
                    tree = ET.parse(kml_file)
                    root = tree.getroot()
                    return root

def load_geojson(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading GeoJSON file: {e}")
        raise HTTPException(status_code=500, detail="Failed to load station data")

# Load DC Metro dataset
# dc_metro_stations = load_geojson('../datasets/Metro_Stations_Regional.geojson')

# if __name__ == "__main__":
#     print(dc_metro_stations)