from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .sentinel_query import query_sentinel_imagery
from .models import AOI, SentinelImagery, SentinelQueryLog, SentinelDownload
from .serializers import AOISerializer, SentinelImagerySerializer, SentinelDownloadSerializer
from .sentinel_api import get_sentinel_image#download_sentinel_image
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import GEOSGeometry
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from shapely.geometry import shape
import json

# Create your views here.
class AOIGeoJSONListView(generics.ListCreateAPIView):
    serializer_class = AOISerializer

    def get_queryset(self):
        return AOI.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AOIDetailView(generics.RetrieveAPIView):
    serializer_class = AOISerializer

    def get_queryset(self):
        return AOI.objects.filter(user=self.request.user)



class SentinelImageryView(APIView):
    def post(self, request):
        try:
            aoi_id = request.data.get("aoi_id")
            start_date = request.data.get("start_date")
            end_date = request.data.get("end_date")
            max_cloud = request.data.get("max_cloud", 30)

            if not all([aoi_id, start_date, end_date]):
                return Response({"error": "Missing fields required"}, status=status.HTTP_400_BAD_REQUEST)
            

            aoi = AOI.objects.get(id=aoi_id, user=request.user)
            geometry = json.loads(aoi.geometry.geojson)

            # Save the query log
            SentinelQueryLog.objects.create(
                aoi=aoi,
                start_date=start_date,
                end_date=end_date,
                max_cloud=max_cloud
            )

            results = query_sentinel_imagery(geometry, start_date, end_date, max_cloud)
            
            saved_entries = []

            for result in results:
                timestamp = datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))
                cloud = result["cloud_coverage"]
                geom_dict = result['geometry']

                # Convert GeoJSON dict to GEOSGeometry for saving to DB
                geom = GEOSGeometry(json.dumps(geom_dict))


                imagery, created = SentinelImagery.objects.get_or_create(
                    aoi=aoi,
                    timestamp=timestamp,
                    geometry=geom,
                    defaults={"cloud_coverage": cloud}
                )
                saved_entries.append({
                    "timestamp": timestamp,
                    "cloud_coverage": cloud,
                    "geometry": geom.wkt,
                    "status": "created" if created else "existing"
                })

            return Response(saved_entries, status=status.HTTP_201_CREATED)
        
        except ObjectDoesNotExist:
            return Response({"error": "AOI not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SentinelImageryGeoJSONView(generics.ListAPIView):
    serializer_class = SentinelImagerySerializer


    def get_queryset(self):
        user = self.request.user

        #Filter the AOI belonging to this user
        user_aois = AOI.objects.filter(user=user)
        queryset = SentinelImagery.objects.filter(aoi__in=user_aois)

        aoi_id = self.request.GET.get("aoi_id")
        if aoi_id and aoi_id.isdigit():
            queryset = queryset.filter(aoi__id=int(aoi_id))
        return queryset


class MapView(LoginRequiredMixin, TemplateView):
    template_name = "geo_processor/map.html"
    login_url = "/api/login/"


@api_view(['GET'])
def query_sentinel_imagery(request, aoi_id):
    try:
        aoi = AOI.objects.get(id=aoi_id, user=request.user)
    except AOI.DoesNotExist:
        return Response({'error': 'AOI not found'}, status=404)
    
    # Retrieve sentinel imagesry entries within this AOI bound
    imagery = SentinelImagery.objects.filter(aoi=aoi)
    serializer = SentinelImagerySerializer(imagery, many=True)

    return Response(serializer.data)


# Update View
@csrf_exempt
def update_aoi(request, aoi_id):
    if request.method == "PATCH":
        try:
            data = json.loads(request.body)
            props = data.get("properties", {})
            aoi = AOI.objects.get(id=aoi_id, user=request.user)
            aoi.name = props.get('name', aoi.name)
            aoi.description = props.get('description', aoi.description)
            aoi.save()
            return JsonResponse({"message": "AOI updated successfully."})
        except AOI.DoesNotExist:
            return JsonResponse({"error": "AOI not found."}, status=404)
    return JsonResponse({"error": "Invalid method."}, status=405)

# Update geometry
@csrf_exempt
def update_aoi_geo(request, aoi_id):
    if request.method == "PATCH":
        try:
            data = json.loads(request.body)
            geojson_geometry = data.get("geometry")

            if not geojson_geometry:
                return JsonResponse({"error": "Missing 'geometry' field."}, status=400)

            aoi = AOI.objects.get(id=aoi_id, user=request.user)

            aoi.geometry = GEOSGeometry(json.dumps(geojson_geometry))
            
            aoi.save()
            return JsonResponse({"message": "AOI geometry updated successfully."})
        except AOI.DoesNotExist:
            return JsonResponse({"error": "AOI not found."}, status=404)
    return JsonResponse({"error": "Invalid method."}, status=405)


# Delete View
@csrf_exempt
def delete_aoi(request, aoi_id):
    if request.method == "DELETE":
        try:
            aoi = AOI.objects.get(id=aoi_id, user=request.user)
            aoi.delete()
            return JsonResponse({"message": "AOI deleted successfully."})
        except AOI.DoesNotExist:
            return JsonResponse({"error": "AOI not found."}, status=404)
    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def download_sentinel_image(request, aoi_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        image_type = data.get('image_type', 'true_color')

        aoi = AOI.objects.get(pk=aoi_id, user=request.user)

        if not aoi.geometry:
            return JsonResponse({'error': 'AOI geometry is missing'}, status=400)

        geometry = json.loads(aoi.geometry.geojson)

        image_bytes = get_sentinel_image(
            geometry=geometry,
            start_date=start_date,
            end_date=end_date,
            image_type=image_type,
        )

        if not image_bytes:
            return JsonResponse({'error': 'Failed to fetch image from Sentinel Hub'}, status=500)
        
        bbox = shape(geometry).bounds

        SentinelDownload.objects.create(
            aoi=aoi,
            start_date=start_date,
            end_date=end_date,
            image_type=image_type,
            bbox={
                "minx": bbox[0],
                "miny": bbox[1],
                "maxx": bbox[2],
                "maxy": bbox[3]
            }
        )

        response = HttpResponse(image_bytes, content_type='image/png')
        response['Content-Disposition'] = 'inline; filename=sentinel_image.png'
        return response

    except AOI.DoesNotExist:
        return JsonResponse({'error': 'AOI not found'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


class SentinelDownloadListView(generics.ListAPIView):
    serializer_class = SentinelDownloadSerializer

    def get_queryset(self):
        queryset = SentinelDownload.objects.all().order_by('-timestamp')
        aoi_id = self.request.GET.get('aoi')
        if aoi_id and aoi_id.isdigit():
            queryset = queryset.filter(aoi__id=int(aoi_id))
        return queryset[:3] # Gives the last three recent download


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("map-view")  # map view
        else:
            return render(request, "geo_processor/login.html", {"error": "Invalid credentials"})
    return render(request, "geo_processor/login.html")

def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "geo_processor/register.html", {"form": form})


# @csrf_exempt
# def download_sentinel_image(request, aoi_id):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             start_date = data.get('start_date')
#             end_date = data.get('end_date')
#             image_type = data.get('image_type', 'true_color')

#             aoi = AOI.objects.get(pk=aoi_id)

#             image_bytes = get_sentinel_image(
#                 geometry=aoi.geometry.geojson,
#                 start_date=start_date,
#                 end_date=end_date,
#                 image_type=image_type,
#             )

#             if not image_bytes:
#                 return JsonResponse({'error': 'Failed to fetch image from Sentinel Hub'}, status=500)

#             response = HttpResponse(image_bytes, content_type='image/png')
#             response['Content-Disposition'] = 'inline; filename=sentinel_image.png'
#             return response

#         except AOI.DoesNotExist:
#             return JsonResponse({'error': 'AOI not found'}, status=404)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Method not allowed'}, status=405)

# def download_sentinel_image_view(request, aoi_id):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Method not allowed"}, status=405)
    
#     try:
#         data = json.loads(request.body)
#         start_date = data['start_date']
#         end_date = data['end_date']
#         bands = data.get('bands', 'TRUE_COLOR')

#         aoi = get_object_or_404(AOI, id=aoi_id)
#         image_bytes = download_sentinel_image(aoi.geometry, start_date, end_date, bands)

#         response = HttpResponse(image_bytes, content_type = 'image/png')
#         response['Content-Disposition'] = f'attachment; filename=sentinel_image_aoi_{aoi_id}.png'
#         return response

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)