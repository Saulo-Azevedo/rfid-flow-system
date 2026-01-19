from django.urls import path

from .views_barcode import (
    api_barcode_dashboard,
    api_registrar_barcode,
    pagina_leitura_barcode,
)

urlpatterns = [
    # Página visual
    path("leitura/", pagina_leitura_barcode, name="pagina_leitura_barcode"),
    # APIs
    path("registrar/", api_registrar_barcode, name="api_registrar_barcode"),
    path("dashboard/", api_barcode_dashboard, name="api_barcode_dashboard"),
]
