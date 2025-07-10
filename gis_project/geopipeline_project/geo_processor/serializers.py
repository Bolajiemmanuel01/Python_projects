# Serializer


from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoFeatureModelListSerializer
from rest_framework import serializers
from .models import AOI, SentinelImagery, SentinelDownload

class AOISerializer(GeoFeatureModelSerializer):
    class Meta:
        model = AOI
        geo_field = "geometry"
        fields = ('id', 'name', 'description', 'geometry', 'uploaded_at')
        list_serializer_class = GeoFeatureModelListSerializer


class SentinelImagerySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = SentinelImagery
        geo_field = "geometry"
        fields = ('id', 'aoi', 'timestamp', 'cloud_coverage', 'geometry', 'queried_at')


class SentinelDownloadSerializer(serializers.ModelSerializer):
    aoi_name = serializers.CharField(source='aoi.name', read_only=True)

    class Meta:
        model = SentinelDownload
        fields = ('id', 'aoi', 'aoi_name', 'start_date', 'end_date', 'image_type', 'timestamp', 'bbox')
