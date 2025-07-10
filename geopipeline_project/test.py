# This file is strictly for testing function within the geo_procssor app

# test_sentinel_auth.py
# from geo_processor.sentinel_auth import get_sentinel_access_token
# import os


# token = get_sentinel_access_token()
# print("Access Token:", token)

from geo_processor.sentinel_query import query_sentinel_imagery

# Example AOI from your earlier upload
aoi_geometry = {
    "type": "Polygon",
    "coordinates": [
        [
            [7.0, 4.0],
            [7.0, 5.0],
            [8.0, 5.0],
            [8.0, 4.0],
            [7.0, 4.0]
        ]
    ]
}

start_date = "2022-01-01"
end_date = "2024-05-01"


results = query_sentinel_imagery(aoi_geometry, start_date, end_date)

for r in results:
    print(f"{r['timestamp']} - Cloud Cover: {r['cloud_coverage']}%")

