from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class AOI(models.Model):    #Area of Interest
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aois', null=False) # User
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    geometry = models.GeometryField(srid=4326)  # Standard spatial ref for Earth

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class SentinelImagery(models.Model):    #Store the data gotten from Sentinel
    aoi = models.ForeignKey(AOI, on_delete=models.CASCADE, related_name='imagery')
    timestamp = models.DateTimeField()
    cloud_coverage = models.FloatField()
    geometry = models.GeometryField()
    queried_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='new')

    class Meta:
        unique_together = ('aoi', 'timestamp')

    def __str__(self):
        return f"{self.aoi.name} - {self.timestamp.date()}"


class SentinelQueryLog(models.Model):
    aoi = models.ForeignKey(AOI, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    max_cloud = models.IntegerField(default=30)
    queried_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query for AOI {self.aoi.name} on {self.queried_at.strftime('%Y-%m-%d %H:%M:%S')}"


class SentinelDownload(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('true_color', 'True Color'),
        ('false_color', 'False Color'),
        ('ndvi', 'NDVI'),
    ]

    aoi = models.ForeignKey(AOI, on_delete=models.CASCADE, related_name="downloads")
    start_date = models.DateField()
    end_date = models.DateField()
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    bbox = models.JSONField(null=True, blank=True)
    image_path = models.CharField(max_length=225, null=True, blank=True)

    def __str__(self):
        return f"{self.aoi.name} - {self.image_type} ({self.start_date} to {self.end_date})"