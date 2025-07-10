# Our Query

import os
import requests
from dotenv import load_dotenv
from geo_processor.sentinel_auth import get_sentinel_access_token

load_dotenv()

def query_sentinel_imagery(aoi_geometry, start_date, end_date, max_cloud=30):
    """
    Queries Sentinel Hub for available Sentinel-2 imagery for a given AOI and date range.
    
    Parameters:
        aoi_geometry (dict): GeoJSON geometry for the Area of Interest (Polygon or MultiPolygon).
        start_date (str): Start of date range (format: YYYY-MM-DD).
        end_date (str): End of date range (format: YYYY-MM-DD).
        max_cloud (int): Maximum cloud coverage percentage.
    
    Returns:
        List of matching image metadata (timestamps, cloud coverage, etc.)
    """
    access_token = get_sentinel_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}", 
        "Content-Type": "application/json"
    }

    COLLECTION_ID = os.getenv("SENTINEL_COLLECTION_ID")

    url = "https://services.sentinel-hub.com/api/v1/catalog/search"

    body = {
        "collections":  [COLLECTION_ID],
        "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
        "limit": 10,
        "intersects": aoi_geometry,
        "query": {
            "eo:cloud_cover": {
                "lt": max_cloud
            }
        }
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status

    features = response.json().get("features", [])
    results= []

    for feature in features:
        results.append({
            "timestamp": feature["properties"]["datetime"],
            "cloud_coverage": feature["properties"].get("eo:cloud_cover"),
            "geometry": feature["geometry"]
        })
    
    return results
