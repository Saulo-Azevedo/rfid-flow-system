from django.contrib import admin
from django.urls import path, include
# from rfid.views import criar_admin_temp

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('rfid.urls')),
    path('api/barcode/', include('rfid.urls_barcode')),
    # path('criar-admin-temp/', criar_admin_temp),
    path('', include('rfid.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
