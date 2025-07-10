# Image Downlaod Helper

import requests
from .sentinel_auth import get_sentinel_access_token
import json

def get_sentinel_image(geometry, start_date, end_date, image_type='true_color'):
    access_token = get_sentinel_access_token()

    evalscripts = {
        'true_color': """
            //VERSION=3
            function setup() {
              return {
                input: ["B04", "B03", "B02"],
                output: { bands: 3 }
              };
            }
            function evaluatePixel(sample) {
              return [sample.B04, sample.B03, sample.B02];
            }
        """,
        'false_color': """
            //VERSION=3
            function setup() {
              return {
                input: ["B08", "B04", "B03"],
                output: { bands: 3 }
              };
            }
            function evaluatePixel(sample) {
              return [sample.B08, sample.B04, sample.B03];
            }
        """,
        'ndvi': """
          //VERSION=3
          function setup() {
            return {
              input: ["B04", "B08"],
              output: { bands: 3 }
            };
          }

          function evaluatePixel(sample) {
            let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
            
            if (ndvi < -0.2) return [0.5, 0.5, 0.5];         // Gray
            else if (ndvi < 0.0) return [0.8, 0.4, 0.4];      // Reddish
            else if (ndvi < 0.2) return [0.9, 0.8, 0.2];      // Yellowish
            else if (ndvi < 0.4) return [0.5, 0.9, 0.4];      // Light Green
            else return [0.2, 0.8, 0.2];                      // Dark Green
          }
        """
    }

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    request_body = {
        "input": {
            "bounds": {
                "geometry": geometry,  # already a dict
                "properties": {
                    "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                }
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": f"{start_date}T00:00:00Z",
                        "to": f"{end_date}T23:59:59Z"
                    },
                    "maxCloudCoverage": 20
                }
            }]
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [{
                "identifier": "default",
                "format": {"type": "image/png"}
            }]
        },
        "evalscript": evalscripts.get(image_type, evalscripts['true_color'])
    }

    response = requests.post(
        url="https://services.sentinel-hub.com/api/v1/process",
        headers={**headers, "Content-Type": "application/json"},
        data=json.dumps(request_body)
    )

    if response.status_code == 200:
        return response.content
    else:
        print("Sentinel Hub Error:")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        return None


# def download_sentinel_image(geometry, start_date, end_date, bands='TRUE_COLOR'):
#     token = get_sentinel_access_token()
#     url = "https://services.sentinel-hub.com/api/v1/process"
#     geometry_dict = json.loads(geometry.json)

#     payload = {
#         "input": {
#             "bounds": {
#                 "geometry": geometry_dict
#             },
#             "data": [{
#                 "type": "S2L2A",
#                 "dataFilter": {
#                     "timeRange": {
#                         "from": start_date + "T00:00:00Z",
#                         "to": end_date + "T23:59:59Z"
#                     }
#                 }
#             }]
#         },
#         "output": {
#             "width": 512,
#             "height": 512,
#             "responses": [{"identifier": "default", "format": {"type": "image/png"}}]
#         },
#         "evalscript": f"""
#         //VERSION=3
#         function setup() {{
#           return {{
#             input: ["B04", "B03", "B02"],
#             output: {{ bands: 3 }}
#           }};
#         }}
#         function evaluatePixel(sample) {{
#           return [sample.B04, sample.B03, sample.B02];
#         }}
#         """
#     }

#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.post(url, json=payload, headers=headers)

#     # DEBUG BLOCK
#     if response.status_code != 200:
#         raise Exception("Failed to fetch image from Sentinel Hub")

#     return response.content


# Grey scale
# 'ndvi': """
#             //VERSION=3
#             function setup() {
#               return {
#                 input: ["B08", "B04"],
#                 output: { bands: 1 }
#               };
#             }
#             function evaluatePixel(sample) {
#               return [(sample.B08 - sample.B04) / (sample.B08 + sample.B04)];
#             }
#         """