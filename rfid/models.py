# rfid/models.py – MODELO FINAL AJUSTADO (com ciclo de Envasadoras + Log de Auditoria)
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone


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
    tag_rfid = models.CharField(max_length=200, unique=True, verbose_name="Tag RFID")

    fabricante = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Fabricante"
    )

    numero_serie = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Número de Série"
    )

    tara = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Tara (kg)"
    )

    # -------- REQUALIFICAÇÃO --------
    data_ultima_requalificacao = models.DateField(
        blank=True, null=True, verbose_name="Última Requalificação"
    )

    data_proxima_requalificacao = models.DateField(
        blank=True, null=True, verbose_name="Próxima Requalificação"
    )

    status_requalificacao = models.CharField(
        max_length=20,
        choices=STATUS_REQUALIFICACAO_CHOICES,
        default="pendente",
        verbose_name="Status da Requalificação",
    )

    # -------- ENVASAMENTO --------
    penultima_envasadora = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Penúltima Envasadora"
    )

    data_penultimo_envasamento = models.DateField(
        blank=True, null=True, verbose_name="Data do Penúltimo Envasamento"
    )

    ultima_envasadora = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Última Envasadora"
    )

    data_ultimo_envasamento = models.DateField(
        blank=True, null=True, verbose_name="Data do Último Envasamento"
    )

    # -------- CONTROLE DO CICLO DE DISTRIBUIDORAS (0..3) --------
    # NULL = ainda não iniciou o ciclo (primeira leitura começa em Distribuidora 1)
    indice_distribuidora = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Índice Distribuidora (0-3)",
        help_text="Controle interno do ciclo de distribuidoras (0..3). NULL = não iniciado.",
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Cadastro"
    )

    # -------- STATUS GERAL --------
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="ativo", verbose_name="Status"
    )

    # -------- ESTATÍSTICAS --------
    total_leituras = models.IntegerField(default=0, verbose_name="Total de Leituras")

    # -------- SOFT DELETE --------
    deletado = models.BooleanField(default=False)
    data_delecao = models.DateTimeField(blank=True, null=True)
    deletado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="botijoes_deletados",
    )
    motivo_delecao = models.TextField(blank=True, null=True)

    # -------- MANAGERS --------
    objects = BotijaoManager()  # sem deletados
    all_objects = models.Manager()  # com deletados

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

    @staticmethod
    def _nome_distribuidora(idx: int) -> str:
        """
        idx: 0..3 -> "Distribuidora 1".."Distribuidora 4"
        """
        return f"Distribuidora {idx + 1}"

    @classmethod
    def avancar_envasadora_por_leitura(cls, botijao_id: int) -> None:
        """
        Atualiza (penúltima/última) envasadora e datas, avançando em ciclo (1..4),
        com lock para evitar corrida quando chegam leituras simultâneas.

        Gera LogAuditoria (acao="leitura") registrando antes/depois.

        - NULL (não iniciado) => primeira leitura: ultima=Distribuidora 1, penultima permanece vazia
        - leituras seguintes: shift e avanço do ciclo
        """
        hoje = timezone.now().date()

        with transaction.atomic():
            botijao = (
                cls.all_objects.select_for_update()
                .only(
                    "id",
                    "tag_rfid",
                    "indice_distribuidora",
                    "ultima_envasadora",
                    "penultima_envasadora",
                    "data_ultimo_envasamento",
                    "data_penultimo_envasamento",
                )
                .get(pk=botijao_id)
            )

            # Snapshot "antes" para auditoria
            antes = {
                "indice_distribuidora": botijao.indice_distribuidora,
                "ultima_envasadora": botijao.ultima_envasadora,
                "penultima_envasadora": botijao.penultima_envasadora,
                "data_ultimo_envasamento": (
                    botijao.data_ultimo_envasamento.isoformat()
                    if botijao.data_ultimo_envasamento
                    else None
                ),
                "data_penultimo_envasamento": (
                    botijao.data_penultimo_envasamento.isoformat()
                    if botijao.data_penultimo_envasamento
                    else None
                ),
            }

            # Determina próximo índice (0..3) e aplica regras
            if botijao.indice_distribuidora is None:
                proximo_idx = 0  # primeira leitura => Distribuidora 1
                # Primeira leitura: NÃO move ultima->penultima (porque ultima pode estar vazia/legada)
                botijao.ultima_envasadora = cls._nome_distribuidora(proximo_idx)
                botijao.data_ultimo_envasamento = hoje
            else:
                proximo_idx = (botijao.indice_distribuidora + 1) % 4

                # Shift: última -> penúltima (e datas)
                botijao.penultima_envasadora = botijao.ultima_envasadora
                botijao.data_penultimo_envasamento = botijao.data_ultimo_envasamento

                # Nova última
                botijao.ultima_envasadora = cls._nome_distribuidora(proximo_idx)
                botijao.data_ultimo_envasamento = hoje

            botijao.indice_distribuidora = proximo_idx

            botijao.save(
                update_fields=[
                    "indice_distribuidora",
                    "ultima_envasadora",
                    "penultima_envasadora",
                    "data_ultimo_envasamento",
                    "data_penultimo_envasamento",
                ]
            )

            # Snapshot "depois" para auditoria
            depois = {
                "indice_distribuidora": botijao.indice_distribuidora,
                "ultima_envasadora": botijao.ultima_envasadora,
                "penultima_envasadora": botijao.penultima_envasadora,
                "data_ultimo_envasamento": (
                    botijao.data_ultimo_envasamento.isoformat()
                    if botijao.data_ultimo_envasamento
                    else None
                ),
                "data_penultimo_envasamento": (
                    botijao.data_penultimo_envasamento.isoformat()
                    if botijao.data_penultimo_envasamento
                    else None
                ),
            }

            # Descrição auditável
            desc = (
                "Envasadora atualizada automaticamente por leitura RFID. "
                f"Última: {depois['ultima_envasadora'] or '-'} "
                f"(antes: {antes['ultima_envasadora'] or '-'}) | "
                f"Penúltima: {depois['penultima_envasadora'] or '-'} "
                f"(antes: {antes['penultima_envasadora'] or '-'})"
            )

            # Cria log (usuario=None por padrão: evento automático)
            LogAuditoria.criar_log(
                botijao=botijao,
                acao="leitura",
                usuario=None,
                descricao=desc,
                dados_anteriores=antes,
                dados_novos=depois,
            )


# ============================================================
# LEITURA RFID
# ============================================================
class LeituraRFID(models.Model):
    botijao = models.ForeignKey(
        Botijao, on_delete=models.CASCADE, related_name="leituras"
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
            # Incrementa contador (como já fazia) — update atômico
            Botijao.all_objects.filter(pk=self.botijao_id).update(
                total_leituras=models.F("total_leituras") + 1
            )

            # Avança ciclo de envasadoras + gera log de auditoria
            Botijao.avancar_envasadora_por_leitura(self.botijao_id)


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

    botijao = models.ForeignKey(Botijao, on_delete=models.CASCADE, related_name="logs")
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
    def criar_log(
        cls,
        botijao,
        acao,
        usuario=None,
        descricao="",
        dados_anteriores=None,
        dados_novos=None,
    ):
        return cls.objects.create(
            botijao=botijao,
            acao=acao,
            usuario=usuario,
            descricao=descricao,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
        )


# ============================================================
# IMPORTAÇÃO XLS
# ============================================================
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


# ============================================================
# LEITURA CÓDIGO DE BARRAS
# ============================================================
class LeituraCodigoBarra(models.Model):
    codigo = models.CharField(max_length=200)
    origem = models.CharField(
        max_length=50,
        default="PDA",
        help_text="Origem da leitura (PDA, manual, outro).",
    )
    operador = models.CharField(max_length=100, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_hora"]

    def __str__(self):
        return f"{self.codigo} – {self.data_hora:%d/%m/%Y %H:%M}"
