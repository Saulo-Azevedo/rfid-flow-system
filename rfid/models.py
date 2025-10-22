from django.db import models
from django.utils import timezone
import uuid

class Botijao(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('manutencao', 'Em Manutenção'),
    ]
    
    # Identificação
    tag_rfid = models.CharField(max_length=100, unique=True, verbose_name='Tag RFID')
    numero_serie = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True,
        verbose_name='Número de Série',
        help_text='Gerado automaticamente se não informado'
    )
    
    # Características
    capacidade = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=13.0, 
        verbose_name='Capacidade (kg)'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='ativo', 
        verbose_name='Status'
    )
    
    # Localização e Cliente
    cliente = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='Cliente',
        help_text='Nome do cliente ou empresa'
    )
    localizacao = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='Localização Atual',
        help_text='Local físico onde o botijão se encontra'
    )
    
    # Observações
    observacao = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Observações',
        help_text='Informações adicionais sobre o botijão'
    )
    
    # Datas
    data_cadastro = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Data de Cadastro'
    )
    ultima_leitura = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='Última Leitura'
    )
    
    # Auditoria - Soft Delete
    deletado = models.BooleanField(default=False, verbose_name='Deletado')
    data_delecao = models.DateTimeField(null=True, blank=True, verbose_name='Data de Exclusão')
    deletado_por = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='botijoes_deletados',
        verbose_name='Deletado por'
    )
    motivo_delecao = models.TextField(blank=True, null=True, verbose_name='Motivo da Exclusão')
    
    class Meta:
        verbose_name = 'Botijão'
        verbose_name_plural = 'Botijões'
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return f"{self.tag_rfid} - {self.numero_serie or 'S/N'}"
    
    def save(self, *args, **kwargs):
        # Gera número de série automaticamente se não informado
        if not self.numero_serie:
            # Formato: BT-ANO-UUID (8 primeiros caracteres)
            ano = timezone.now().year
            uuid_part = str(uuid.uuid4())[:8].upper()
            self.numero_serie = f"BT-{ano}-{uuid_part}"
        super().save(*args, **kwargs)
    
    @property
    def historico(self):
        """Retorna todas as leituras deste botijão"""
        return self.leituras.all().order_by('-data_hora')
    
    def soft_delete(self, user=None, motivo=''):
        """Marca o botijão como deletado sem remover do banco"""
        self.deletado = True
        self.data_delecao = timezone.now()
        self.deletado_por = user
        self.motivo_delecao = motivo
        self.status = 'inativo'
        self.save()
    
    def restaurar(self):
        """Restaura um botijão deletado"""
        self.deletado = False
        self.data_delecao = None
        self.deletado_por = None
        self.motivo_delecao = None
        self.status = 'ativo'
        self.save()
    
    def registrar_leitura(self, operador='', observacao='', localizacao='', request=None):
        """Registra uma nova leitura para este botijão"""
        from .utils.audit_log import registrar_leitura_rfid
        
        # Verifica duplicação (mesma tag em menos de 5 segundos)
        ultimo = self.leituras.first()
        if ultimo:
            diff = timezone.now() - ultimo.data_hora
            if diff.total_seconds() < 5:
                return ultimo  # Retorna a leitura anterior (deduplicação)
        
        # Atualiza localização do botijão se informada
        if localizacao:
            self.localizacao = localizacao
            self.save(update_fields=['localizacao'])
        
        # Cria nova leitura
        leitura = Leitura.objects.create(
            botijao=self,
            tag_rfid=self.tag_rfid,
            operador=operador,
            observacao=observacao,
            localizacao=localizacao or self.localizacao or ''
        )
        
        # Atualiza última leitura do botijão
        self.ultima_leitura = leitura.data_hora
        self.save(update_fields=['ultima_leitura'])
        
        # Registra no log de auditoria
        registrar_leitura_rfid(
            usuario=None,
            objeto=leitura,
            detalhes=f'Leitura RFID do botijão {self.tag_rfid}. Operador: {operador or "Não informado"}. Local: {localizacao or "Não informado"}',
            request=request
        )
        
        return leitura
    
    @property
    def total_leituras(self):
        """Retorna o total de leituras deste botijão"""
        return self.leituras.count() 
        
class Leitura(models.Model):
    """Histórico de leituras RFID"""
    
    botijao = models.ForeignKey(Botijao, on_delete=models.CASCADE, related_name='leituras')
    tag_rfid = models.CharField(max_length=50, db_index=True, verbose_name='Tag RFID')
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')
    operador = models.CharField(max_length=100, blank=True, verbose_name='Operador')
    localizacao = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='Localização',
        help_text='Local onde a leitura foi realizada'
    )
    observacao = models.TextField(blank=True, verbose_name='Observação')
    
    class Meta:
        ordering = ['-data_hora']
        verbose_name = "Leitura"
        verbose_name_plural = "Leituras"
        indexes = [
            models.Index(fields=['-data_hora']),
            models.Index(fields=['tag_rfid']),
        ]
    
    def __str__(self):
        return f"{self.tag_rfid[:15]}... - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"

class ConfiguracaoSistema(models.Model):
    """Configurações gerais do sistema"""
    
    email_relatorios = models.EmailField(blank=True, verbose_name="Email para Relatórios")
    enviar_relatorio_diario = models.BooleanField(default=False, verbose_name="Enviar Relatório Diário")
    alerta_dias_sem_leitura = models.IntegerField(default=30, verbose_name="Alerta - Dias sem Leitura")
    
    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"
    
    def __str__(self):
        return "Configurações do Sistema"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        config, created = cls.objects.get_or_create(pk=1)
        return config

class LogAuditoria(models.Model):
    ACAO_CHOICES = [
        ('criar', 'Criado'),
        ('editar', 'Editado'),
        ('deletar', 'Deletado'),
        ('restaurar', 'Restaurado'),
        ('leitura', 'Leitura RFID'),
    ]
    
    usuario = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Usuário'
    )
    acao = models.CharField(max_length=20, choices=ACAO_CHOICES, verbose_name='Ação')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    objeto_id = models.IntegerField(verbose_name='ID do Objeto')
    objeto_repr = models.CharField(max_length=200, verbose_name='Representação do Objeto')
    detalhes = models.TextField(blank=True, null=True, verbose_name='Detalhes')
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Endereço IP')
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['-data_hora']),
            models.Index(fields=['modelo', 'objeto_id']),
        ]
    
    def __str__(self):
        usuario_nome = self.usuario.username if self.usuario else 'Sistema'
        return f"{self.get_acao_display()} - {self.modelo} #{self.objeto_id} por {usuario_nome}"