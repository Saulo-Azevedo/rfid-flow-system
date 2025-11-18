# rfid/urls.py - URLs COMPLETAS E ORGANIZADAS DO SISTEMA RFID FLOW

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    # ========================================
    # 🔐 AUTENTICAÇÃO
    # ========================================
    path('login/', 
         auth_views.LoginView.as_view(template_name='login.html'), 
         name='login'),
    
    path('logout/', 
         auth_views.LogoutView.as_view(next_page='login'), 
         name='logout'),
    
    
    # ========================================
    # 🔑 RECUPERAÇÃO DE SENHA
    # ========================================
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
    
    
    # ========================================
    # 🏠 PÁGINAS PRINCIPAIS DO SISTEMA
    # ========================================
    path('', views.dashboard, name='dashboard'),
    path('nova-leitura/', views.nova_leitura, name='nova_leitura'),
    path('relatorios/', views.relatorios, name='relatorios'),
    
    
    # ========================================
    # 📊 HISTÓRICO E BUSCA
    # ========================================
    # ⚠️ IMPORTANTE: Ordem importa! 
    # /historico/buscar/ deve vir ANTES de /botijao/<id>/historico/
    # senão Django tenta interpretar "buscar" como um ID
    
    path('historico/buscar/', views.buscar_historico, name='buscar_historico'),  # ✅ Rota principal
    path('historico/', views.buscar_historico, name='historico_busca'),  # Alias para compatibilidade
    path('botijao/<int:botijao_id>/historico/', views.historico_botijao, name='historico_botijao'),
    
    
    # ========================================
    # 📤 EXPORTAR E ENVIAR RELATÓRIOS
    # ========================================
    path('exportar-excel/', views.exportar_excel, name='exportar_excel'),
    path('enviar-email/', views.enviar_email_view, name='enviar_email'),  # ✅ Nome principal
    path('enviar-relatorio/', views.enviar_email_view, name='enviar_relatorio'),  # Alias para compatibilidade
    
    
    # ========================================
    # 🔌 APIs AJAX (Atualização em Tempo Real)
    # ========================================
    path('api/dashboard/', views.dashboard_api, name='dashboard_api'),
    path('api/relatorios/', views.relatorios_api, name='relatorios_api'),
    
    
    # ========================================
    # 📡 API PARA INTEGRAÇÃO RFID
    # ========================================
    path('api/registrar-leitura/', views.api_registrar_leitura, name='api_registrar_leitura'),
    
    
    # ========================================
    # 🔧 UTILITÁRIOS (DESENVOLVIMENTO)
    # ========================================
    # ⚠️ DESCOMENTE APENAS TEMPORARIAMENTE PARA CRIAR ADMIN INICIAL
    # ⚠️ DEPOIS COMENTE NOVAMENTE POR SEGURANÇA!
    # path('criar-admin-temp/', views.criar_admin_temp, name='criar_admin_temp'),
]

'''

## 📋 **MAPA COMPLETO DAS ROTAS**

### **🔐 Autenticação**
```
/login/                           → Login do sistema
/logout/                          → Logout do sistema
```

### **🔑 Recuperação de Senha**
```
/password-reset/                  → Solicitar reset de senha
/password-reset/done/             → Confirmação de email enviado
/password-reset-confirm/<uid>/<token>/ → Definir nova senha
/password-reset-complete/         → Senha alterada com sucesso
```

### **🏠 Páginas Principais**
```
/                                 → Dashboard (home)
/nova-leitura/                   → Formulário nova leitura RFID
/relatorios/                     → Relatórios com filtros
```

### **📊 Histórico**
```
/historico/buscar/               → 🆕 Buscar histórico (PRINCIPAL)
/historico/                      → Alias (compatibilidade)
/botijao/123/historico/          → Histórico completo de um botijão
```

### **📤 Exportar/Enviar**
```
/exportar-excel/                 → Download Excel
/enviar-email/                   → Enviar por e-mail (PRINCIPAL)
/enviar-relatorio/               → Alias (compatibilidade)
```

### **🔌 APIs AJAX**
```
/api/dashboard/                  → Dados para dashboard
/api/relatorios/                 → Dados para relatórios
```

### **📡 API RFID**
```
/api/registrar-leitura/          → Registrar leitura via POST

'''