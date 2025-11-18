# rfid/models.py - MODELO AJUSTADO
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class BotijaoManager(models.Manager):
    """Manager customizado que exclui registros deletados"""
    def get_queryset(self):
        return super().get_queryset().filter(deletado=False)


class Botijao(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('manutencao', 'Em Manutenção'),
    ]
    
    STATUS_REQUALIFICACAO_CHOICES = [
        ('em_dia', 'Em Dia'),
        ('proximo_vencimento', 'Próximo ao Vencimento'),
        ('vencida', 'Vencida'),
        ('pendente', 'Pendente'),
    ]
    
    # === IDENTIFICAÇÃO ===
    tag_rfid = models.CharField(
        max_length=200, 
        unique=True, 
        verbose_name='Tag RFID',
        help_text='Código único da tag RFID'
    )
    
    # ⚠️ AJUSTE 1: Número de série NÃO é mais gerado automaticamente
    numero_serie = models.CharField(
        max_length=100, 
        unique=True, 
        blank=True,  # Permite vazio
        null=True,   # Permite NULL no banco
        verbose_name='Número de Série',
        help_text='Número de série do botijão (informar manualmente)'
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='ativo', 
        verbose_name='Status'
    )
    
    # ⚠️ AJUSTE 2: Capacidade SEM valor padrão
    capacidade = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='Capacidade (kg)',
        blank=True,  # Campo opcional
        null=True,   # Permite NULL
        help_text='Capacidade em kg (ex: 13.00, 20.00, 45.00)'
        # REMOVIDO: default=13.0
    )
    
    # === LOCALIZAÇÃO E CLIENTE ===
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
        verbose_name='Localização',
        help_text='Endereço ou localização atual do botijão'
    )
    
    observacao = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Observações',
        help_text='Informações adicionais sobre o botijão'
    )
    
    # === DATAS ===
    data_cadastro = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Data de Cadastro'
    )
    
    data_atualizacao = models.DateTimeField(
        auto_now=True, 
        verbose_name='Última Atualização'
    )
    
    # === CAMPOS REGULATÓRIOS ANP ===
    fabricante = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name='Fabricante'
    )
    
    ano_fabricacao = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name='Ano de Fabricação'
    )
    
    data_ultima_requalificacao = models.DateField(
        blank=True, 
        null=True, 
        verbose_name='Última Requalificação'
    )
    
    data_proxima_requalificacao = models.DateField(
        blank=True, 
        null=True, 
        verbose_name='Próxima Requalificação'
    )
    
    status_requalificacao = models.CharField(
        max_length=20,
        choices=STATUS_REQUALIFICACAO_CHOICES,
        default='pendente',
        verbose_name='Status Requalificação'
    )
    
    certificado_inmetro = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Certificado INMETRO'
    )
    
    # === INFORMAÇÕES OPERACIONAIS ===
    peso_vazio = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Peso Vazio (kg)',
        help_text='Peso do botijão vazio (tara)'
    )
    
    peso_cheio = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Peso Cheio (kg)',
        help_text='Peso do botijão cheio'
    )
    
    pressao_teste = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Pressão de Teste (bar)',
        help_text='Pressão de teste hidrostático'
    )
    
    lote_fabricacao = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Lote de Fabricação'
    )
    
    # === ESTATÍSTICAS (calculadas) ===
    total_leituras = models.IntegerField(
        default=0,
        verbose_name='Total de Leituras',
        help_text='Contador automático de leituras'
    )
    
    total_enchimentos = models.IntegerField(
        default=0,
        verbose_name='Total de Enchimentos',
        help_text='Número de vezes que foi enchido'
    )
    
    total_km_percorridos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='KM Percorridos',
        help_text='Estimativa de distância percorrida'
    )
    
    # === SOFT DELETE ===
    deletado = models.BooleanField(
        default=False, 
        verbose_name='Deletado'
    )
    
    data_delecao = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name='Data de Exclusão'
    )
    
    deletado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='botijoes_deletados',
        verbose_name='Deletado por'
    )
    
    motivo_delecao = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Motivo da Exclusão'
    )
    
    # === MANAGERS ===
    objects = BotijaoManager()  # Manager padrão (sem deletados)
    all_objects = models.Manager()  # Manager que retorna tudo
    
    class Meta:
        verbose_name = 'Botijão'
        verbose_name_plural = 'Botijões'
        ordering = ['-data_cadastro']
        indexes = [
            models.Index(fields=['tag_rfid']),
            models.Index(fields=['numero_serie']),
            models.Index(fields=['status', 'deletado']),
            models.Index(fields=['data_proxima_requalificacao']),
        ]
    
    def __str__(self):
        return f"{self.tag_rfid} - {self.numero_serie or 'Sem série'}"
    
    # ⚠️ AJUSTE 1: REMOVIDO o método save() que gerava número de série automático
    # Agora o número de série deve ser informado manualmente
    
    @property
    def ultima_leitura(self):
        """Retorna a última leitura deste botijão"""
        leitura = self.leituras.order_by('-data_hora').first()
        return leitura.data_hora if leitura else None
    
    @property
    def dias_para_requalificacao(self):
        """Calcula quantos dias faltam para a requalificação"""
        if not self.data_proxima_requalificacao:
            return None
        
        delta = self.data_proxima_requalificacao - timezone.now().date()
        return delta.days
    
    @property
    def requalificacao_vencida(self):
        """Verifica se a requalificação está vencida"""
        if not self.data_proxima_requalificacao:
            return False
        
        return timezone.now().date() > self.data_proxima_requalificacao
    
    def atualizar_status_requalificacao(self):
        """Atualiza automaticamente o status de requalificação"""
        if not self.data_proxima_requalificacao:
            self.status_requalificacao = 'pendente'
        elif self.requalificacao_vencida:
            self.status_requalificacao = 'vencida'
        elif self.dias_para_requalificacao <= 90:  # 90 dias antes
            self.status_requalificacao = 'proximo_vencimento'
        else:
            self.status_requalificacao = 'em_dia'
        
        self.save(update_fields=['status_requalificacao'])
    
    def deletar(self, usuario, motivo=''):
        """Realiza soft delete do botijão"""
        self.deletado = True
        self.data_delecao = timezone.now()
        self.deletado_por = usuario
        self.motivo_delecao = motivo
        self.save()
    
    def restaurar(self):
        """Restaura um botijão deletado"""
        self.deletado = False
        self.data_delecao = None
        self.deletado_por = None
        self.motivo_delecao = ''
        self.save()


class LeituraRFID(models.Model):
    """Modelo para registrar cada leitura RFID"""
    
    botijao = models.ForeignKey(
        Botijao,
        on_delete=models.CASCADE,
        related_name='leituras',
        verbose_name='Botijão'
    )
    
    data_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora da Leitura'
    )
    
    operador = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Operador',
        help_text='Nome do operador que fez a leitura'
    )
    
    localizacao_leitura = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Localização da Leitura',
        help_text='Local onde foi feita a leitura'
    )
    
    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações',
        help_text='Observações sobre esta leitura específica'
    )
    
    # Dados técnicos da leitura RFID
    rssi = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='RSSI',
        help_text='Força do sinal RFID'
    )
    
    antena = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Antena',
        help_text='Número da antena que fez a leitura'
    )
    
    leitor_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID do Leitor',
        help_text='Identificador do dispositivo leitor'
    )
    
    class Meta:
        verbose_name = 'Leitura RFID'
        verbose_name_plural = 'Leituras RFID'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['botijao', '-data_hora']),
            models.Index(fields=['-data_hora']),
        ]
    
    def __str__(self):
        return f"{self.botijao.tag_rfid} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        """Incrementa contador de leituras do botijão"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Incrementa total de leituras
            self.botijao.total_leituras += 1
            self.botijao.save(update_fields=['total_leituras'])


class LogAuditoria(models.Model):
    """Log de auditoria para rastrear ações importantes"""
    
    ACAO_CHOICES = [
        ('criar', 'Criar'),
        ('atualizar', 'Atualizar'),
        ('deletar', 'Deletar'),
        ('restaurar', 'Restaurar'),
        ('leitura', 'Leitura RFID'),
    ]
    
    botijao = models.ForeignKey(
        Botijao,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Botijão'
    )
    
    acao = models.CharField(
        max_length=20,
        choices=ACAO_CHOICES,
        verbose_name='Ação'
    )
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuário'
    )
    
    data_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora'
    )
    
    descricao = models.TextField(
        verbose_name='Descrição'
    )
    
    dados_anteriores = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Dados Anteriores',
        help_text='Estado anterior do objeto (JSON)'
    )
    
    dados_novos = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Dados Novos',
        help_text='Novo estado do objeto (JSON)'
    )
    
    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['botijao', '-data_hora']),
            models.Index(fields=['acao', '-data_hora']),
        ]
    
    def __str__(self):
        return f"{self.acao} - {self.botijao.tag_rfid} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def criar_log(cls, botijao, acao, usuario=None, descricao='', dados_anteriores=None, dados_novos=None):
        """Método helper para criar logs"""
        return cls.objects.create(
            botijao=botijao,
            acao=acao,
            usuario=usuario,
            descricao=descricao,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos
        )