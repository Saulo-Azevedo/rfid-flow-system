from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Recuperação de Senha
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html',
             email_template_name='password_reset_email.html',
             subject_template_name='password_reset_subject.txt'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Páginas do sistema
    path('', views.dashboard, name='dashboard'),
    path('nova-leitura/', views.nova_leitura, name='nova_leitura'),
    path('historico/', views.historico_busca, name='historico_busca'),
    path('botijao/<int:botijao_id>/historico/', views.historico_botijao, name='historico_botijao'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('exportar-excel/', views.exportar_excel, name='exportar_excel'),
    path('enviar-relatorio/', views.enviar_relatorio_view, name='enviar_relatorio'),
    
    # API para registrar leitura RFID
    path('api/registrar-leitura/', views.api_registrar_leitura, name='api_registrar_leitura'),
    
    # APIs para AJAX (atualização em tempo real)
    path('api/dashboard/', views.dashboard_api, name='dashboard_api'),
    path('api/relatorios/', views.relatorios_api, name='relatorios_api'),
]