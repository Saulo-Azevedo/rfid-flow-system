# rfid/urls.py - URLs COMPLETAS E ORGANIZADAS DO SISTEMA RFID FLOW

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .views_import import confirmar_import, preview_import, upload_xls

urlpatterns = [
    # ========================================
    # 🔐 AUTENTICAÇÃO
    # ========================================
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    # ========================================
    # 🔑 RECUPERAÇÃO DE SENHA
    # ========================================
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html",
            email_template_name="password_reset_email.txt",  # texto (fallback)
            html_email_template_name="password_reset_email.html",  # HTML de verdade ✅
            subject_template_name="password_reset_subject.txt",
            success_url="/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html",
            success_url="/password-reset-complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # ========================================
    # 🏠 PÁGINAS PRINCIPAIS DO SISTEMA
    # ========================================
    path("", views.dashboard, name="dashboard"),
    path("nova-leitura/", views.nova_leitura, name="nova_leitura"),
    path("relatorios/", views.relatorios, name="relatorios"),
    # ========================================
    # 📊 HISTÓRICO E BUSCA
    # ========================================
    # ⚠️ IMPORTANTE: Ordem importa!
    # /historico/buscar/ deve vir ANTES de /botijao/<id>/historico/
    # senão Django tenta interpretar "buscar" como um ID
    path(
        "historico/buscar/", views.buscar_historico, name="buscar_historico"
    ),  # ✅ Rota principal
    path(
        "historico/", views.buscar_historico, name="historico_busca"
    ),  # Alias para compatibilidade
    path(
        "botijao/<int:botijao_id>/historico/",
        views.historico_botijao,
        name="historico_botijao",
    ),
    # ========================================
    # 📤 EXPORTAR E ENVIAR RELATÓRIOS
    # ========================================
    path("exportar-excel/", views.exportar_excel, name="exportar_excel"),
    path(
        "enviar-email/", views.enviar_email_view, name="enviar_email"
    ),  # ✅ Nome principal
    path(
        "enviar-relatorio/", views.enviar_email_view, name="enviar_relatorio"
    ),  # Alias para compatibilidade
    # ========================================
    # 🔌 APIs AJAX (Atualização em Tempo Real)
    # ========================================
    path("api/dashboard/", views.dashboard_api, name="dashboard_api"),
    path("api/relatorios/", views.relatorios_api, name="relatorios_api"),
    # ========================================
    # 📡 API PARA INTEGRAÇÃO RFID
    # ========================================
    path(
        "api/registrar-leitura/",
        views.api_registrar_leitura,
        name="api_registrar_leitura",
    ),
    # ========================================
    # 🔧 UTILITÁRIOS (DESENVOLVIMENTO)
    # ========================================
    # ⚠️ DESCOMENTE APENAS TEMPORARIAMENTE PARA CRIAR ADMIN INICIAL
    # ⚠️ DEPOIS COMENTE NOVAMENTE POR SEGURANÇA!
    # path('criar-admin-temp/', views.criar_admin_temp, name='criar_admin_temp'),
    # rota onde o usuário envia o arquivo
    path("upload-xls/", upload_xls, name="upload_xls"),
    path("preview-import/", preview_import, name="preview_import"),
    # rota da confirmação
    path("confirmar-import/", confirmar_import, name="confirmar_import"),
]
