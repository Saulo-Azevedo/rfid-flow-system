# rfid/admin.py - ADMIN AJUSTADO COM FIELDSETS COLAPSÁVEIS

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Botijao, LeituraRFID, LogAuditoria


@admin.register(Botijao)
class BotijaoAdmin(admin.ModelAdmin):
    """Admin customizado para Botijão"""
    
    # ⚠️ AJUSTE 3: Adicionando colapso para "Informações Operacionais"
    fieldsets = (
        ('📋 Identificação', {
            'fields': ('tag_rfid', 'numero_serie', 'status', 'capacidade'),
            'description': 'Informações básicas de identificação do botijão'
        }),
        ('👤 Cliente e Localização', {
            'fields': ('cliente', 'localizacao', 'observacao'),
            'classes': ('collapse',),  # Colapsado por padrão
        }),
        ('🏭 Dados Regulatórios ANP/INMETRO', {
            'fields': (
                'fabricante',
                'ano_fabricacao',
                'certificado_inmetro',
                'lote_fabricacao',
            ),
            'classes': ('collapse',),  # Colapsado por padrão
        }),
        ('📅 Requalificação', {
            'fields': (
                'data_ultima_requalificacao',
                'data_proxima_requalificacao',
                'status_requalificacao',
            ),
            'classes': ('collapse',),  # Colapsado por padrão
        }),
        ('⚙️ Informações Operacionais', {
            'fields': (
                'peso_vazio',
                'peso_cheio',
                'pressao_teste',
            ),
            'classes': ('collapse',),  # ✅ COLAPSO ADICIONADO!
            'description': 'Dados técnicos operacionais do botijão'
        }),
        ('📊 Estatísticas', {
            'fields': (
                'total_leituras',
                'total_enchimentos',
                'total_km_percorridos',
            ),
            'classes': ('collapse',),  # Colapsado por padrão
        }),
        ('🗑️ Exclusão (Soft Delete)', {
            'fields': (
                'deletado',
                'data_delecao',
                'deletado_por',
                'motivo_delecao',
            ),
            'classes': ('collapse',),  # Colapsado por padrão
        }),
    )
    
    list_display = (
        'tag_rfid_colored',
        'numero_serie_display',
        'status_badge',
        'capacidade_display',
        'cliente_display',
        'total_leituras',
        'requalificacao_badge',
        'data_cadastro_display',
    )
    
    list_filter = (
        'status',
        'status_requalificacao',
        'deletado',
        'data_cadastro',
        'fabricante',
    )
    
    search_fields = (
        'tag_rfid',
        'numero_serie',
        'cliente',
        'localizacao',
        'certificado_inmetro',
    )
    
    readonly_fields = (
        'data_cadastro',
        'data_atualizacao',
        'total_leituras',
    )
    
    list_per_page = 50
    date_hierarchy = 'data_cadastro'
    
    actions = [
        'marcar_como_ativo',
        'marcar_como_inativo',
        'marcar_como_manutencao',
        'atualizar_status_requalificacao',
        'deletar_selecionados',
        'restaurar_selecionados',
    ]
    
    # === MÉTODOS PERSONALIZADOS PARA DISPLAY ===
    
    @admin.display(description='Tag RFID', ordering='tag_rfid')
    def tag_rfid_colored(self, obj):
        """Tag RFID colorida"""
        color = '#00D4FF' if obj.status == 'ativo' else '#FF6B6B'
        return format_html(
            '<strong style="color: {};">{}</strong>',
            color,
            obj.tag_rfid
        )
    
    @admin.display(description='Nº Série')
    def numero_serie_display(self, obj):
        """Exibe número de série ou mensagem padrão"""
        if obj.numero_serie:
            return obj.numero_serie
        return format_html('<em style="color: #999;">Sem série</em>')
    
    @admin.display(description='Status')
    def status_badge(self, obj):
        """Badge visual do status"""
        colors = {
            'ativo': '#00E676',
            'inativo': '#FF3D00',
            'manutencao': '#FFD600',
        }
        
        labels = {
            'ativo': 'Ativo',
            'inativo': 'Inativo',
            'manutencao': 'Manutenção',
        }
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#999'),
            labels.get(obj.status, obj.status)
        )
    
    @admin.display(description='Capacidade')
    def capacidade_display(self, obj):
        """Exibe capacidade formatada"""
        if obj.capacidade:
            return f"{obj.capacidade} kg"
        return format_html('<em style="color: #999;">Não informada</em>')
    
    @admin.display(description='Cliente')
    def cliente_display(self, obj):
        """Exibe cliente ou mensagem padrão"""
        if obj.cliente:
            return obj.cliente
        return format_html('<em style="color: #999;">Sem cliente</em>')
    
    @admin.display(description='Requalificação')
    def requalificacao_badge(self, obj):
        """Badge do status de requalificação"""
        if not obj.data_proxima_requalificacao:
            return format_html(
                '<span style="background-color: #999; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 10px;">Pendente</span>'
            )
        
        colors = {
            'em_dia': '#00E676',
            'proximo_vencimento': '#FFD600',
            'vencida': '#FF3D00',
            'pendente': '#999',
        }
        
        labels = {
            'em_dia': 'Em Dia',
            'proximo_vencimento': 'Próx. Venc.',
            'vencida': 'Vencida',
            'pendente': 'Pendente',
        }
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 10px;">{}</span>',
            colors.get(obj.status_requalificacao, '#999'),
            labels.get(obj.status_requalificacao, 'Pendente')
        )
    
    @admin.display(description='Data Cadastro', ordering='data_cadastro')
    def data_cadastro_display(self, obj):
        """Formata data de cadastro"""
        return obj.data_cadastro.strftime('%d/%m/%Y %H:%M')
    
    # === ACTIONS PERSONALIZADAS ===
    
    @admin.action(description='✅ Marcar como Ativo')
    def marcar_como_ativo(self, request, queryset):
        """Marca botijões como ativo"""
        count = queryset.update(status='ativo')
        self.message_user(request, f'{count} botijão(ões) marcado(s) como ATIVO.')
    
    @admin.action(description='❌ Marcar como Inativo')
    def marcar_como_inativo(self, request, queryset):
        """Marca botijões como inativo"""
        count = queryset.update(status='inativo')
        self.message_user(request, f'{count} botijão(ões) marcado(s) como INATIVO.')
    
    @admin.action(description='🔧 Marcar como Manutenção')
    def marcar_como_manutencao(self, request, queryset):
        """Marca botijões em manutenção"""
        count = queryset.update(status='manutencao')
        self.message_user(request, f'{count} botijão(ões) marcado(s) em MANUTENÇÃO.')
    
    @admin.action(description='📅 Atualizar Status de Requalificação')
    def atualizar_status_requalificacao(self, request, queryset):
        """Atualiza automaticamente status de requalificação"""
        count = 0
        for botijao in queryset:
            botijao.atualizar_status_requalificacao()
            count += 1
        self.message_user(request, f'{count} botijão(ões) atualizado(s).')
    
    @admin.action(description='🗑️ Deletar Selecionados (Soft Delete)')
    def deletar_selecionados(self, request, queryset):
        """Realiza soft delete dos botijões selecionados"""
        count = 0
        for botijao in queryset.filter(deletado=False):
            botijao.deletar(usuario=request.user, motivo='Deletado via admin')
            count += 1
        self.message_user(request, f'{count} botijão(ões) deletado(s).')
    
    @admin.action(description='♻️ Restaurar Selecionados')
    def restaurar_selecionados(self, request, queryset):
        """Restaura botijões deletados"""
        count = 0
        for botijao in queryset.filter(deletado=True):
            botijao.restaurar()
            count += 1
        self.message_user(request, f'{count} botijão(ões) restaurado(s).')
    
    def get_queryset(self, request):
        """Mostra todos os objetos, incluindo deletados no admin"""
        return self.model.all_objects.get_queryset()


@admin.register(LeituraRFID)
class LeituraRFIDAdmin(admin.ModelAdmin):
    """Admin para Leituras RFID"""
    
    list_display = (
        'botijao_link',
        'data_hora_display',
        'operador',
        'localizacao_leitura',
        'rssi_display',
        'antena',
        'leitor_id',
    )
    
    list_filter = (
        'data_hora',
        'operador',
        'antena',
        'leitor_id',
    )
    
    search_fields = (
        'botijao__tag_rfid',
        'botijao__numero_serie',
        'operador',
        'localizacao_leitura',
        'observacao',
    )
    
    readonly_fields = ('data_hora',)
    
    date_hierarchy = 'data_hora'
    list_per_page = 100
    
    fieldsets = (
        ('📋 Informações Básicas', {
            'fields': ('botijao', 'data_hora', 'operador'),
        }),
        ('📍 Localização', {
            'fields': ('localizacao_leitura', 'observacao'),
        }),
        ('📡 Dados Técnicos RFID', {
            'fields': ('rssi', 'antena', 'leitor_id'),
            'classes': ('collapse',),
        }),
    )
    
    @admin.display(description='Botijão', ordering='botijao__tag_rfid')
    def botijao_link(self, obj):
        """Link para o botijão"""
        return format_html(
            '<a href="/admin/rfid/botijao/{}/change/" style="color: #00D4FF; font-weight: bold;">{}</a>',
            obj.botijao.id,
            obj.botijao.tag_rfid
        )
    
    @admin.display(description='Data/Hora', ordering='data_hora')
    def data_hora_display(self, obj):
        """Formata data/hora"""
        return obj.data_hora.strftime('%d/%m/%Y %H:%M:%S')
    
    @admin.display(description='RSSI')
    def rssi_display(self, obj):
        """Exibe RSSI com indicador visual"""
        if obj.rssi is None:
            return '-'
        
        # RSSI típico: -30 (excelente) a -90 (ruim)
        if obj.rssi > -40:
            color = '#00E676'  # Verde
            label = 'Excelente'
        elif obj.rssi > -60:
            color = '#FFD600'  # Amarelo
            label = 'Bom'
        else:
            color = '#FF3D00'  # Vermelho
            label = 'Fraco'
        
        return format_html(
            '<span style="color: {};">{} dBm ({})</span>',
            color,
            obj.rssi,
            label
        )


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    """Admin para Logs de Auditoria"""
    
    list_display = (
        'botijao_link',
        'acao_badge',
        'usuario',
        'data_hora_display',
        'descricao_resumida',
    )
    
    list_filter = (
        'acao',
        'data_hora',
        'usuario',
    )
    
    search_fields = (
        'botijao__tag_rfid',
        'botijao__numero_serie',
        'descricao',
        'usuario__username',
    )
    
    readonly_fields = (
        'botijao',
        'acao',
        'usuario',
        'data_hora',
        'descricao',
        'dados_anteriores',
        'dados_novos',
    )
    
    date_hierarchy = 'data_hora'
    list_per_page = 100
    
    def has_add_permission(self, request):
        """Não permite adicionar logs manualmente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Não permite deletar logs"""
        return False
    
    @admin.display(description='Botijão', ordering='botijao__tag_rfid')
    def botijao_link(self, obj):
        """Link para o botijão"""
        return format_html(
            '<a href="/admin/rfid/botijao/{}/change/" style="color: #00D4FF;">{}</a>',
            obj.botijao.id,
            obj.botijao.tag_rfid
        )
    
    @admin.display(description='Ação')
    def acao_badge(self, obj):
        """Badge visual da ação"""
        colors = {
            'criar': '#00E676',
            'atualizar': '#00D4FF',
            'deletar': '#FF3D00',
            'restaurar': '#FFD600',
            'leitura': '#9C27B0',
        }
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            colors.get(obj.acao, '#999'),
            obj.get_acao_display()
        )
    
    @admin.display(description='Data/Hora', ordering='data_hora')
    def data_hora_display(self, obj):
        """Formata data/hora"""
        return obj.data_hora.strftime('%d/%m/%Y %H:%M:%S')
    
    @admin.display(description='Descrição')
    def descricao_resumida(self, obj):
        """Resumo da descrição"""
        if len(obj.descricao) > 60:
            return obj.descricao[:60] + '...'
        return obj.descricao


# Customização do Admin Site
admin.site.site_header = 'RFID Flow - Administração'
admin.site.site_title = 'RFID Flow Admin'
admin.site.index_title = 'Painel de Controle'