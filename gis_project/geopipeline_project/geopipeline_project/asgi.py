"""
ASGI config for geopipeline_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""
import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

from django.core.asgi import get_asgi_application



os.environ["GDAL_LIBRARY_PATH"] = str(Path("C:/OSGeo4W64/bin/gdal310.dll"))
os.environ["GEOS_LIBRARY_PATH"] = str(Path("C:/OSGeo4W64/bin/geos_c.dll"))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geopipeline_project.settings')

application = get_asgi_application()
