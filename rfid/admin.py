from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Botijao, Leitura, ConfiguracaoSistema, LogAuditoria
from .utils.audit_log import registrar_criacao, registrar_edicao, registrar_delecao, registrar_restauracao


@admin.register(Botijao)
class BotijaoAdmin(admin.ModelAdmin):
    list_display = ['tag_rfid', 'numero_serie', 'cliente', 'localizacao', 'status_badge', 'ultima_leitura', 'deletado_badge']
    list_filter = ['status', 'deletado', 'data_cadastro', 'cliente']
    search_fields = ['tag_rfid', 'numero_serie', 'cliente', 'localizacao']
    readonly_fields = ['numero_serie', 'data_cadastro', 'ultima_leitura', 'data_delecao', 'deletado_por']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('tag_rfid', 'numero_serie', 'capacidade', 'status')
        }),
        ('Cliente e Localização', {
            'fields': ('cliente', 'localizacao', 'observacao')
        }),
        ('Datas', {
            'fields': ('data_cadastro', 'ultima_leitura')
        }),
        ('Auditoria de Exclusão', {
            'fields': ('deletado', 'data_delecao', 'deletado_por', 'motivo_delecao'),
            'classes': ('collapse',),
            'description': 'Informações sobre exclusão (soft delete)'
        }),
    )
    
    actions = ['soft_delete_selected', 'restaurar_selected']
    
    def status_badge(self, obj):
        colors = {
            'ativo': '#28a745',
            'inativo': '#dc3545',
            'manutencao': '#ffc107'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def deletado_badge(self, obj):
        if obj.deletado:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px; font-weight: 600;">🗑️ DELETADO</span>'
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px; font-weight: 600;">✅ ATIVO</span>'
        )
    deletado_badge.short_description = 'Estado'
    
    def soft_delete_selected(self, request, queryset):
        """Marca os botijões selecionados como deletados"""
        count = 0
        for botijao in queryset.filter(deletado=False):
            botijao.soft_delete(user=request.user, motivo='Exclusão em lote via admin')
            registrar_delecao(
                usuario=request.user,
                objeto=botijao,
                detalhes='Exclusão em lote via admin',
                request=request
            )
            count += 1
        
        self.message_user(request, f'{count} botijão(ões) marcado(s) como deletado(s).')
    soft_delete_selected.short_description = '🗑️ Marcar como deletado (Soft Delete)'
    
    def restaurar_selected(self, request, queryset):
        """Restaura botijões deletados"""
        count = 0
        for botijao in queryset.filter(deletado=True):
            botijao.restaurar()
            registrar_restauracao(
                usuario=request.user,
                objeto=botijao,
                detalhes='Restauração via admin',
                request=request
            )
            count += 1
        
        self.message_user(request, f'{count} botijão(ões) restaurado(s).')
    restaurar_selected.short_description = '♻️ Restaurar botijões deletados'
    
    def save_model(self, request, obj, form, change):
        """Registra criação/edição no log"""
        if change:
            super().save_model(request, obj, form, change)
            registrar_edicao(
                usuario=request.user,
                objeto=obj,
                detalhes=f'Editado via admin. Campos alterados: {", ".join(form.changed_data)}',
                request=request
            )
        else:
            super().save_model(request, obj, form, change)
            registrar_criacao(
                usuario=request.user,
                objeto=obj,
                detalhes='Criado via admin',
                request=request
            )
    
    def get_queryset(self, request):
        """Mostra TODOS os botijões (incluindo deletados) no admin"""
        qs = super().get_queryset(request)
        return qs


@admin.register(Leitura)
class LeituraAdmin(admin.ModelAdmin):
    list_display = ['tag_rfid', 'botijao_link', 'data_hora', 'operador', 'localizacao']
    list_filter = ['data_hora', 'localizacao', 'operador']
    search_fields = ['tag_rfid', 'botijao__numero_serie', 'operador', 'localizacao', 'observacao']
    readonly_fields = ['data_hora']
    date_hierarchy = 'data_hora'
    
    fieldsets = (
        ('Informações da Leitura', {
            'fields': ('botijao', 'tag_rfid', 'data_hora')
        }),
        ('Detalhes', {
            'fields': ('operador', 'localizacao', 'observacao')
        }),
    )
    
    def botijao_link(self, obj):
        if obj.botijao:
            url = f'/admin/rfid/botijao/{obj.botijao.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.botijao)
        return '-'
    botijao_link.short_description = 'Botijão'


@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(admin.ModelAdmin):
    list_display = ['email_relatorios', 'enviar_relatorio_diario', 'alerta_dias_sem_leitura']
    
    fieldsets = (
        ('Configurações de E-mail', {
            'fields': ('email_relatorios', 'enviar_relatorio_diario')
        }),
        ('Alertas', {
            'fields': ('alerta_dias_sem_leitura',)
        }),
    )
    
    def has_add_permission(self, request):
        # Só permite 1 configuração
        return not ConfiguracaoSistema.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Não permite deletar a configuração
        return False

@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ['data_hora', 'usuario_nome', 'acao_badge', 'modelo', 'objeto_repr', 'ip_address']
    list_filter = ['acao', 'modelo', 'data_hora', 'usuario']
    search_fields = ['objeto_repr', 'detalhes', 'usuario__username']
    readonly_fields = ['usuario', 'acao', 'modelo', 'objeto_id', 'objeto_repr', 'detalhes', 'data_hora', 'ip_address']
    date_hierarchy = 'data_hora'
    
    fieldsets = (
        ('Informações da Ação', {
            'fields': ('usuario', 'acao', 'data_hora', 'ip_address')
        }),
        ('Objeto Afetado', {
            'fields': ('modelo', 'objeto_id', 'objeto_repr')
        }),
        ('Detalhes', {
            'fields': ('detalhes',),
            'classes': ('collapse',)
        }),
    )
    
    def usuario_nome(self, obj):
        if obj.usuario:
            return obj.usuario.username
        return '🤖 Sistema'
    usuario_nome.short_description = 'Usuário'
    
    def acao_badge(self, obj):
        colors = {
            'criar': '#28a745',
            'editar': '#ffc107',
            'deletar': '#dc3545',
            'restaurar': '#17a2b8',
            'leitura': '#6f42c1'
        }
        icons = {
            'criar': '➕',
            'editar': '✏️',
            'deletar': '🗑️',
            'restaurar': '♻️',
            'leitura': '📡'
        }
        color = colors.get(obj.acao, '#6c757d')
        icon = icons.get(obj.acao, '❓')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: 600;">{} {}</span>',
            color,
            icon,
            obj.get_acao_display()
        )
    acao_badge.short_description = 'Ação'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return False


# Customização do Admin
admin.site.site_header = "Sistema RFID - Administração"
admin.site.site_title = "RFID Admin"
admin.site.index_title = "Gerenciamento de Botijões e Auditoria"