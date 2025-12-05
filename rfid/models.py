# rfid/models.py – MODELO FINAL AJUSTADO
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# ============================================================
# GERENCIADOR PARA SOFT DELETE
# ============================================================
class BotijaoManager(models.Manager):
    """Retorna apenas botijões não deletados."""
    def get_queryset(self):
        return super().get_queryset().filter(deletado=False)


# ============================================================
# BOTIJÃO (CILINDRO)
# ============================================================
class Botijao(models.Model):

    # -------- STATUS --------
    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("inativo", "Inativo"),
        ("manutencao", "Manutenção"),
    ]

    STATUS_REQUALIFICACAO_CHOICES = [
        ("em_dia", "Em Dia"),
        ("proximo_vencimento", "Próximo ao Vencimento"),
        ("vencida", "Vencida"),
        ("pendente", "Pendente"),
    ]

    # -------- CAMPOS PRINCIPAIS --------
    tag_rfid = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Tag RFID"
    )

    fabricante = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Fabricante"
    )

    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Série"
    )

    tara = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Tara (kg)"
    )

    # -------- REQUALIFICAÇÃO --------
    data_ultima_requalificacao = models.DateField(
        blank=True,
        null=True,
        verbose_name="Última Requalificação"
    )

    data_proxima_requalificacao = models.DateField(
        blank=True,
        null=True,
        verbose_name="Próxima Requalificação"
    )

    status_requalificacao = models.CharField(
        max_length=20,
        choices=STATUS_REQUALIFICACAO_CHOICES,
        default="pendente",
        verbose_name="Status da Requalificação"
    )

    # -------- ENVASAMENTO --------
    penultima_envasadora = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Penúltima Envasadora"
    )

    data_penultimo_envasamento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data do Penúltimo Envasamento"
    )

    ultima_envasadora = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Última Envasadora"
    )

    data_ultimo_envasamento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data do Último Envasamento"
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )

    # -------- STATUS GERAL --------
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ativo",
        verbose_name="Status"
    )

    # -------- ESTATÍSTICAS --------
    total_leituras = models.IntegerField(
        default=0,
        verbose_name="Total de Leituras"
    )

    # -------- SOFT DELETE --------
    deletado = models.BooleanField(default=False)
    data_delecao = models.DateTimeField(blank=True, null=True)
    deletado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="botijoes_deletados"
    )
    motivo_delecao = models.TextField(blank=True, null=True)

    # -------- MANAGERS --------
    objects = BotijaoManager()       # sem deletados
    all_objects = models.Manager()   # com deletados

    # ============================================================
    # META
    # ============================================================
    class Meta:
        verbose_name = "Botijão"
        verbose_name_plural = "Botijões"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["tag_rfid"]),
            models.Index(fields=["numero_serie"]),
            models.Index(fields=["status"]),
        ]

    # ============================================================
    # MÉTODOS
    # ============================================================
    def __str__(self):
        return f"{self.tag_rfid} – {self.numero_serie or 'Sem Série'}"

    @property
    def ultima_leitura(self):
        """Retorna a última leitura registrada."""
        leitura = self.leituras.order_by("-data_hora").first()
        return leitura.data_hora if leitura else None

    def deletar(self, usuario, motivo=""):
        self.deletado = True
        self.data_delecao = timezone.now()
        self.deletado_por = usuario
        self.motivo_delecao = motivo
        self.save()

    def restaurar(self):
        self.deletado = False
        self.data_delecao = None
        self.deletado_por = None
        self.motivo_delecao = ""
        self.save()


# ============================================================
# LEITURA RFID
# ============================================================
class LeituraRFID(models.Model):
    botijao = models.ForeignKey(
        Botijao,
        on_delete=models.CASCADE,
        related_name="leituras"
    )

    data_hora = models.DateTimeField(auto_now_add=True)
    operador = models.CharField(max_length=100, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)

    # dados técnicos opcionais
    rssi = models.IntegerField(blank=True, null=True)
    antena = models.IntegerField(blank=True, null=True)
    leitor_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["-data_hora"]

    def __str__(self):
        return f"{self.botijao.tag_rfid} – {self.data_hora:%d/%m/%Y %H:%M}"

    def save(self, *args, **kwargs):
        novo = self.pk is None
        super().save(*args, **kwargs)
        if novo:
            self.botijao.total_leituras += 1
            self.botijao.save(update_fields=["total_leituras"])


# ============================================================
# LOG DE AUDITORIA
# ============================================================
class LogAuditoria(models.Model):
    ACAO_CHOICES = [
        ("criar", "Criar"),
        ("atualizar", "Atualizar"),
        ("deletar", "Deletar"),
        ("restaurar", "Restaurar"),
        ("leitura", "Leitura RFID"),
    ]

    botijao = models.ForeignKey(
        Botijao,
        on_delete=models.CASCADE,
        related_name="logs"
    )
    acao = models.CharField(max_length=20, choices=ACAO_CHOICES)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField()
    dados_anteriores = models.JSONField(blank=True, null=True)
    dados_novos = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-data_hora"]

    def __str__(self):
        return f"{self.acao} – {self.botijao.tag_rfid}"

    @classmethod
    def criar_log(cls, botijao, acao, usuario=None, descricao="", dados_anteriores=None, dados_novos=None):
        return cls.objects.create(
            botijao=botijao,
            acao=acao,
            usuario=usuario,
            descricao=descricao,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos
        )
class ImportacaoXLS(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    arquivo_nome = models.CharField(max_length=300)
    data_hora = models.DateTimeField(auto_now_add=True)

    total_linhas = models.IntegerField(default=0)
    leituras_importadas = models.IntegerField(default=0)
    novos_botijoes = models.IntegerField(default=0)
    duplicados_ignorados = models.IntegerField(default=0)

    erros = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-data_hora"]


# rfid/models.py

class LeituraCodigoBarra(models.Model):
    codigo = models.CharField(max_length=200)
    origem = models.CharField(
        max_length=50,
        default="PDA",
        help_text="Origem da leitura (PDA, manual, outro)."
    )
    operador = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    observacao = models.TextField(
        blank=True,
        null=True
    )
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_hora"]

    def __str__(self):
        return f"{self.codigo} – {self.data_hora:%d/%m/%Y %H:%M}"
