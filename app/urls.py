from django.contrib import admin
from django.urls import path, include
from rfid.views import criar_admin_temp

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('rfid.urls')),
    path('criar-admin-temp/', criar_admin_temp),  # ⬆️ ADICIONE ESTA LINHA
    path('', include('rfid.urls')),
]