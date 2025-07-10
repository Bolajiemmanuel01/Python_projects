# geo_processor urls file

from django.urls import path
from .views import AOIGeoJSONListView, AOIDetailView, SentinelImageryView, SentinelImageryGeoJSONView, MapView, SentinelDownloadListView, query_sentinel_imagery, update_aoi, delete_aoi, update_aoi_geo, download_sentinel_image, register_view, logout_view, login_view




urlpatterns = [
    path('aois/', AOIGeoJSONListView.as_view(), name='aoi-list'),
    path('aois/<int:pk>/', AOIDetailView.as_view(), name='aoi-detail'),
    path('sentinel-imagery/', SentinelImageryView.as_view(), name='sentinel-imagery'),
    path("sentinel-imagery-geo/", SentinelImageryGeoJSONView.as_view(), name="sentinel-imagery-geo"),
    path("map/", MapView.as_view(), name="map-view"),
    path('query-sentinel/<int:aoi_id>/', query_sentinel_imagery, name='query_sentinel_imagery'),
    path("aois/<int:aoi_id>/update/", update_aoi, name="update_aoi"),
    path("aois/<int:aoi_id>/delete/", delete_aoi, name="delete_aoi"),
    path("aois/<int:aoi_id>/updategeo/", update_aoi_geo, name="update_aoi_geo"),
    path("aois/<int:aoi_id>/download/", download_sentinel_image, name="download-sentinel-image"),
    path("downloads/", SentinelDownloadListView.as_view(), name='sentinel-download-list'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path("register/", register_view, name="register"),
]