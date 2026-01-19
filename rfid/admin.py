# rfid/admin.py — VERSÃO AJUSTADA E COMPATÍVEL
from django.contrib import admin

from .models import Botijao, LeituraRFID, LogAuditoria


# ============================================================
# BOTIJÃO
# ============================================================
@admin.register(Botijao)
class BotijaoAdmin(admin.ModelAdmin):
    list_display = [
        "tag_rfid",
        "fabricante",
        "numero_serie",
        "tara",
        "status",
        "status_requalificacao",
        "data_ultima_requalificacao",
        "data_proxima_requalificacao",
        "ultima_envasadora",
        "data_ultimo_envasamento",
        "total_leituras",
        "deletado",
    ]

    list_filter = [
        "fabricante",
        "status",
        "status_requalificacao",
        "deletado",
    ]

    search_fields = [
        "tag_rfid",
        "numero_serie",
        "fabricante",
    ]

    readonly_fields = [
        "data_delecao",
        "deletado_por",
        "total_leituras",
    ]

    fieldsets = (
        (
            "Identificação",
            {
                "fields": (
                    "tag_rfid",
                    "fabricante",
                    "numero_serie",
                    "tara",
                    "status",
                )
            },
        ),
        (
            "Requalificação",
            {
                "fields": (
                    "data_ultima_requalificacao",
                    "data_proxima_requalificacao",
                    "status_requalificacao",
                )
            },
        ),
        (
            "Envasamento",
            {
                "fields": (
                    "penultima_envasadora",
                    "data_penultimo_envasamento",
                    "ultima_envasadora",
                    "data_ultimo_envasamento",
                )
            },
        ),
        ("Estatísticas", {"fields": ("total_leituras",)}),
        (
            "Soft Delete",
            {
                "classes": ("collapse",),
                "fields": (
                    "deletado",
                    "data_delecao",
                    "deletado_por",
                    "motivo_delecao",
                ),
            },
        ),
    )


# ============================================================
# LEITURA RFID
# ============================================================
@admin.register(LeituraRFID)
class LeituraRFIDAdmin(admin.ModelAdmin):
    list_display = [
        "botijao",
        "data_hora",
        "operador",
        "rssi",
        "antena",
        "leitor_id",
    ]

    list_filter = ["data_hora", "operador"]
    search_fields = ["botijao__tag_rfid", "operador"]


# ============================================================
# LOG DE AUDITORIA
# ============================================================
@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ["botijao", "acao", "usuario", "data_hora"]
    list_filter = ["acao", "usuario"]
    search_fields = ["botijao__tag_rfid", "descricao"]
