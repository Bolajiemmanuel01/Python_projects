from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import AOI, SentinelImagery, SentinelQueryLog, SentinelDownload

# Register your models here.
@admin.register(AOI)
class MyGeoModelAdmin(GISModelAdmin):
    list_display = ('name',)

@admin.register(SentinelImagery)
class SentinelImageryAdmin(GISModelAdmin):
    list_display = ('aoi', 'timestamp', 'cloud_coverage', 'status')
    list_filter = ('status',)
    search_fields = ('aoi__name',)
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

@admin.register(SentinelQueryLog)
class SentinelQueryLogAdmin(admin.ModelAdmin):
    list_display = ('aoi', 'queried_at',)

@admin.register(SentinelDownload)
class SentinelDownloadAdmin(admin.ModelAdmin):
    list_display = ('aoi', 'image_type', 'start_date', 'end_date', 'timestamp')
    list_filter = ('image_type', 'timestamp')
    search_fields = ('aoi__name',)