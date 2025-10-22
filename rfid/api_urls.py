from django.urls import path
from . import views

urlpatterns = [
    path('registrar-leitura/', views.api_registrar_leitura, name='api_registrar_leitura'),
]