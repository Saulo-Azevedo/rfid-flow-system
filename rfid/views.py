# rfid/views.py

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from .models import Botijao, LeituraRFID, LogAuditoria
from .forms import BotijaoForm


# -----------------------
# Helpers de requalificação
# -----------------------

def _classificar_requal(botijao, hoje):
    """
    Retorna um rótulo simples para o status da requalificação:
    vencida / proxima / em_dia / sem_data
    """
    proxima = botijao.data_proxima_requalificacao
    if not proxima:
        return "sem_data"
    if proxima <= hoje:
        return "vencida"
    if hoje < proxima <= hoje + timedelta(days=90):
        return "proxima"
    return "em_dia"


# -----------------------
# Dashboard
# -----------------------

@login_required
def dashboard(request):
    hoje = timezone.now().date()

    # Estatísticas principais
    total_botijoes = Botijao.objects.filter(deletado=False).count()
    leituras_hoje = LeituraRFID.objects.filter(data_hora__date=hoje).count()
    
    # Botijões ativos = próximos da requalificação ou dentro da validade
    botijoes_ativos = Botijao.objects.filter(
        deletado=False
    ).exclude(status_requalificacao="vencida").count()

    # --- Últimos botijões cadastrados + total de leituras ---
    botijoes = (
        Botijao.objects
        .filter(deletado=False)
        .annotate(num_leituras=Count("leituras"))
        .order_by("-id")[:10]
    )

    # --- Leituras dos últimos 7 dias (gráfico e estatísticas futuras) ---
    leituras_7_dias = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        leituras_7_dias.append({
            "data": dia.strftime("%d/%m"),
            "total": LeituraRFID.objects.filter(data_hora__date=dia).count()
        })

    # Requalificação
    cilindros = Botijao.objects.filter(deletado=False)
    requal_vencidas = []
    requal_proximas = []
    requal_em_dia = []
    requal_sem_data = []

    for c in cilindros:
        status = _classificar_requal(c, hoje)
        if status == "vencida":
            requal_vencidas.append(c)
        elif status == "proxima":
            requal_proximas.append(c)
        elif status == "em_dia":
            requal_em_dia.append(c)
        else:
            requal_sem_data.append(c)

    # Últimas leituras
    ultimas_leituras = (
        LeituraRFID.objects
        .select_related("botijao")
        .order_by("-data_hora")[:10]
    )

    # CONTEXTO FINAL — **somente UM return**, no fim!
    context = {
        "total_botijoes": total_botijoes,
        "leituras_hoje": leituras_hoje,
        "botijoes_ativos": botijoes_ativos,

        "botijoes": botijoes,
        "ultimas_leituras": ultimas_leituras,

        "leituras_7_dias": leituras_7_dias,

        "qtd_requal_vencidas": len(requal_vencidas),
        "qtd_requal_proximas": len(requal_proximas),
        "qtd_requal_em_dia": len(requal_em_dia),
        "qtd_requal_sem_data": len(requal_sem_data),
    }

    return render(request, "rfid/dashboard.html", context)


@login_required
def dashboard_api(request):
    """Versão JSON do dashboard para uso com AJAX, se necessário."""
    hoje = timezone.now().date()

    total_cilindros = Botijao.objects.filter(deletado=False).count()
    total_leituras_hoje = LeituraRFID.objects.filter(data_hora__date=hoje).count()

    leituras_7_dias = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        count = LeituraRFID.objects.filter(data_hora__date=dia).count()
        leituras_7_dias.append({
            "data": dia.strftime("%d/%m"),
            "total": count,
        })

    cilindros = list(Botijao.objects.filter(deletado=False))
    requal_vencidas = []
    requal_proximas = []
    requal_em_dia = []
    requal_sem_data = []

    for c in cilindros:
        status = _classificar_requal(c, hoje)
        if status == "vencida":
            requal_vencidas.append(c)
        elif status == "proxima":
            requal_proximas.append(c)
        elif status == "em_dia":
            requal_em_dia.append(c)
        else:
            requal_sem_data.append(c)

    requal_proximas_ordenadas = sorted(
        requal_proximas,
        key=lambda x: x.data_proxima_requalificacao or hoje
    )[:10]

    proximas_data = [
        {
            "tag_rfid": c.tag_rfid,
            "fabricante": c.fabricante or "-",
            "numero_serie": c.numero_serie or "-",
            "data_ultima_requalificacao": c.data_ultima_requalificacao.strftime("%d/%m/%Y")
            if c.data_ultima_requalificacao else "-",
            "data_proxima_requalificacao": c.data_proxima_requalificacao.strftime("%d/%m/%Y")
            if c.data_proxima_requalificacao else "-",
        }
        for c in requal_proximas_ordenadas
    ]

    return JsonResponse({
        "total_cilindros": total_cilindros,
        "total_leituras_hoje": total_leituras_hoje,
        "leituras_7_dias": leituras_7_dias,
        "qtd_requal_vencidas": len(requal_vencidas),
        "qtd_requal_proximas": len(requal_proximas),
        "qtd_requal_em_dia": len(requal_em_dia),
        "qtd_requal_sem_data": len(requal_sem_data),
        "requal_proximas": proximas_data,
    })


# -----------------------
# Cadastro / edição de Botijão
# -----------------------

@login_required
def novo_botijao(request):
    if request.method == "POST":
        form = BotijaoForm(request.POST)
        if form.is_valid():
            botijao = form.save()
            messages.success(request, f"Botijão {botijao.tag_rfid} cadastrado com sucesso.")
            return redirect("dashboard")
    else:
        form = BotijaoForm()

    return render(request, "botijao_form.html", {"form": form})


@login_required
def editar_botijao(request, botijao_id):
    botijao = get_object_or_404(Botijao, pk=botijao_id, deletado=False)

    if request.method == "POST":
        form = BotijaoForm(request.POST, instance=botijao)
        if form.is_valid():
            form.save()
            messages.success(request, f"Botijão {botijao.tag_rfid} atualizado com sucesso.")
            return redirect("historico_botijao", botijao_id=botijao.id)
    else:
        form = BotijaoForm(instance=botijao)

    return render(request, "botijao_form.html", {"form": form, "botijao": botijao})


# -----------------------
# Leitura RFID manual
# -----------------------

@login_required
def nova_leitura(request):
    if request.method == "POST":
        tag_rfid = request.POST.get("tag_rfid", "").strip()
        operador = request.POST.get("operador", "").strip()
        observacao = request.POST.get("observacao", "").strip()

        if not tag_rfid:
            messages.error(request, "Tag RFID é obrigatória.")
            return redirect("nova_leitura")

        botijao, criado = Botijao.objects.get_or_create(tag_rfid=tag_rfid)

        leitura = LeituraRFID.objects.create(
            botijao=botijao,
            operador=operador or None,
            observacao=observacao or None,
        )

        try:
            LogAuditoria.criar_log(
                botijao=botijao,
                acao="leitura",
                usuario=request.user if request.user.is_authenticated else None,
                descricao=f"Leitura manual registrada. Observação: {observacao or '-'}",
                dados_anteriores=None,
                dados_novos={"leitura_id": leitura.id},
            )
        except Exception:
            pass

        if criado:
            messages.success(
                request,
                f"Novo botijão cadastrado e leitura registrada. Tag: {tag_rfid}",
            )
        else:
            messages.success(request, f"Leitura registrada. Tag: {tag_rfid}")

        return redirect("dashboard")

    return render(request, "nova_leitura.html")


# -----------------------
# Relatórios de requalificação e leituras
# -----------------------

@login_required
def relatorios(request):
    status = request.GET.get("status", "")
    data_inicio = request.GET.get("data_inicio", "")
    data_fim = request.GET.get("data_fim", "")

    botijoes = (
        Botijao.objects.filter(deletado=False)
        .annotate(num_leituras=Count("leituras"))
    )

    # FILTRO POR STATUS
    if status:
        botijoes = botijoes.filter(status=status)

    # FILTROS POR DATA DE CADASTRO
    if data_inicio:
        botijoes = botijoes.filter(data_cadastro__date__gte=data_inicio)

    if data_fim:
        botijoes = botijoes.filter(data_cadastro__date__lte=data_fim)

    botijoes = botijoes.order_by("-data_cadastro")

    # TOTAL DE LEITURAS SOMADAS
    total_leituras = sum([b.num_leituras for b in botijoes])

    context = {
        "botijoes": botijoes,
        "total_filtrado": botijoes.count(),
        "total_leituras": total_leituras,
        "status_choices": Botijao.STATUS_CHOICES,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "status_selected": status,
    }

    return render(request, "rfid/relatorios.html", context)


@login_required
def relatorios_api(request):
    status = request.GET.get("status", "")
    data_inicio = request.GET.get("data_inicio", "")
    data_fim = request.GET.get("data_fim", "")

    qs = (
        Botijao.objects.filter(deletado=False)
        .annotate(num_leituras=Count("leituras"))
    )

    if status:
        qs = qs.filter(status=status)

    if data_inicio:
        qs = qs.filter(data_cadastro__date__gte=data_inicio)

    if data_fim:
        qs = qs.filter(data_cadastro__date__lte=data_fim)

    qs = qs.order_by("-data_cadastro")

    botijoes_data = []
    for b in qs:
        botijoes_data.append({
            "tag_rfid": b.tag_rfid,
            "numero_serie": b.numero_serie or "-",
            "fabricante": b.fabricante or "-",
            "status_display": b.get_status_display(),
            "status_requalificacao_display": b.get_status_requalificacao_display(),
            "total_leituras": b.num_leituras,
            "data_cadastro": b.data_cadastro.strftime("%d/%m/%Y %H:%M"),
        })

    return JsonResponse({
        "botijoes": botijoes_data,
        "total_filtrado": qs.count()
    })



# -----------------------
# Exportar Excel
# -----------------------

@login_required
def exportar_excel(request):
    hoje = timezone.now().date()

    wb = Workbook()
    ws = wb.active
    ws.title = "Cilindros RFID"

    headers = [
        "Tag RFID",
        "Fabricante",
        "Número de Série",
        "Tara (kg)",
        "Última requalificação",
        "Próxima requalificação",
        "Dias para requalificação",
        "Status requalificação",
        "Penúltima envasadora",
        "Data penúltimo envasamento",
        "Última envasadora",
        "Data último envasamento",
    ]
    ws.append(headers)

    header_fill = PatternFill(start_color="00D4FF", end_color="00D4FF", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    cilindros = Botijao.objects.filter(deletado=False).order_by("tag_rfid")

    for c in cilindros:
        status = _classificar_requal(c, hoje)
        dias = None
        if c.data_proxima_requalificacao:
            dias = (c.data_proxima_requalificacao - hoje).days

        ws.append([
            c.tag_rfid,
            c.fabricante or "-",
            c.numero_serie or "-",
            float(c.tara) if c.tara is not None else "-",
            c.data_ultima_requalificacao.strftime("%d/%m/%Y")
            if c.data_ultima_requalificacao else "-",
            c.data_proxima_requalificacao.strftime("%d/%m/%Y")
            if c.data_proxima_requalificacao else "-",
            dias if dias is not None else "-",
            status,
            c.penultima_envasadora or "-",
            c.data_penultimo_envasamento.strftime("%d/%m/%Y")
            if c.data_penultimo_envasamento else "-",
            c.ultima_envasadora or "-",
            c.data_ultimo_envasamento.strftime("%d/%m/%Y")
            if c.data_ultimo_envasamento else "-",
        ])

    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except Exception:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"relatorio_cilindros_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


# -----------------------
# Histórico por botijão
# -----------------------

@login_required
def historico_botijao(request, botijao_id):
    botijao = get_object_or_404(Botijao, id=botijao_id, deletado=False)
    leituras = (
        LeituraRFID.objects
        .filter(botijao=botijao)
        .order_by("-data_hora")
    )
    context = {
        "botijao": botijao,
        "leituras": leituras,
    }
    return render(request, "historico_botijao.html", context)


@login_required
def buscar_historico(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    status_requal = request.GET.get("status_requal", "")
    data_req_inicio = request.GET.get("data_req_inicio", "")
    data_req_fim = request.GET.get("data_req_fim", "")
    data_env_inicio = request.GET.get("data_env_inicio", "")
    data_env_fim = request.GET.get("data_env_fim", "")
    operador = request.GET.get("operador", "").strip()

    resultados = []

    qs = Botijao.objects.filter(deletado=False).annotate(
        num_leituras=Count("leituras")
    ).prefetch_related("leituras")

    # -------------------------
    # 🔍 Filtros Avançados
    # -------------------------

    if query:
        qs = qs.filter(
            Q(tag_rfid__icontains=query) |
            Q(numero_serie__icontains=query) |
            Q(fabricante__icontains=query)
        )

    if status:
        qs = qs.filter(status=status)

    if status_requal:
        qs = qs.filter(status_requalificacao=status_requal)

    if data_req_inicio:
        qs = qs.filter(data_ultima_requalificacao__gte=data_req_inicio)

    if data_req_fim:
        qs = qs.filter(data_ultima_requalificacao__lte=data_req_fim)

    if data_env_inicio:
        qs = qs.filter(data_ultimo_envasamento__gte=data_env_inicio)

    if data_env_fim:
        qs = qs.filter(data_ultimo_envasamento__lte=data_env_fim)

    # -------------------------
    # 🔍 Filtrar por OPERADOR
    # -------------------------
    if operador:
        qs = qs.filter(leituras__operador__icontains=operador).distinct()

    # -------------------------
    # 🔍 Montagem dos Resultados
    # -------------------------

    for b in qs:
        leituras = list(b.leituras.order_by("-data_hora")[:10])

        leituras_data = [
            {
                "data_hora": l.data_hora.strftime("%d/%m/%Y %H:%M:%S"),
                "operador": l.operador or "-",
                "observacao": l.observacao or "-",
            }
            for l in leituras
        ]

        resultados.append({
            "botijao": {
                "id": b.id,
                "tag_rfid": b.tag_rfid,
                "numero_serie": b.numero_serie or "-",
                "fabricante": b.fabricante or "-",
                "tara": b.tara or "-",
                "data_ultima_requalificacao": b.data_ultima_requalificacao,
                "data_proxima_requalificacao": b.data_proxima_requalificacao,
                "status_requalificacao_display": b.get_status_requalificacao_display(),
                "penultima_envasadora": b.penultima_envasadora or "-",
                "data_penultimo_envasamento": b.data_penultimo_envasamento,
                "ultima_envasadora": b.ultima_envasadora or "-",
                "data_ultimo_envasamento": b.data_ultimo_envasamento,
                "status": b.get_status_display(),
            },
            "leituras": leituras_data,
            "total_leituras": b.num_leituras,
        })

    context = {
        "query": query,
        "resultados": resultados,
        "total_encontrados": len(resultados),
        "status_choices": Botijao.STATUS_CHOICES,
        "status_requal_choices": Botijao.STATUS_REQUALIFICACAO_CHOICES,
    }

    return render(request, "historico_busca.html", context)


# -----------------------
# Enviar relatório por e-mail
# -----------------------

@login_required
def enviar_email_view(request):
    if request.method == "POST":
        destinatario = request.POST.get("destinatario", "").strip()

        if not destinatario:
            messages.error(request, "Email de destinatário é obrigatório.")
            return redirect("enviar_email")

        try:
            from io import BytesIO

            hoje = timezone.now().date()

            wb = Workbook()
            ws = wb.active
            ws.title = "Cilindros RFID"

            headers = [
                "Tag RFID",
                "Fabricante",
                "Número de Série",
                "Tara (kg)",
                "Última requalificação",
                "Próxima requalificação",
                "Dias para requalificação",
                "Status requalificação",
                "Penúltima envasadora",
                "Data penúltimo envasamento",
                "Última envasadora",
                "Data último envasamento",
            ]
            ws.append(headers)

            header_fill = PatternFill(start_color="00D4FF", end_color="00D4FF", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)

            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            cilindros = Botijao.objects.filter(deletado=False).order_by("tag_rfid")

            for c in cilindros:
                status = _classificar_requal(c, hoje)
                dias = None
                if c.data_proxima_requalificacao:
                    dias = (c.data_proxima_requalificacao - hoje).days

                ws.append([
                    c.tag_rfid,
                    c.fabricante or "-",
                    c.numero_serie or "-",
                    float(c.tara) if c.tara is not None else "-",
                    c.data_ultima_requalificacao.strftime("%d/%m/%Y")
                    if c.data_ultima_requalificacao else "-",
                    c.data_proxima_requalificacao.strftime("%d/%m/%Y")
                    if c.data_proxima_requalificacao else "-",
                    dias if dias is not None else "-",
                    status,
                    c.penultima_envasadora or "-",
                    c.data_penultimo_envasamento.strftime("%d/%m/%Y")
                    if c.data_penultimo_envasamento else "-",
                    c.ultima_envasadora or "-",
                    c.data_ultimo_envasamento.strftime("%d/%m/%Y")
                    if c.data_ultimo_envasamento else "-",
                ])

            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except Exception:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width

            excel_buffer = BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)

            data_hora_str = timezone.now().strftime("%d/%m/%Y às %H:%M")
            filename = f"relatorio_cilindros_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            total_cilindros = cilindros.count()
            total_leituras = LeituraRFID.objects.count()

            corpo_html = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: #f5f5f5;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 10px;
                        overflow: hidden;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #00D4FF 0%, #7FFF00 100%);
                        padding: 30px;
                        text-align: center;
                        color: white;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                    }}
                    .content {{
                        padding: 30px;
                    }}
                    .stats {{
                        display: grid;
                        grid-template-columns: repeat(3, 1fr);
                        gap: 15px;
                        margin: 20px 0;
                    }}
                    .stat-card {{
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 8px;
                        text-align: center;
                    }}
                    .stat-value {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #00D4FF;
                    }}
                    .stat-label {{
                        font-size: 12px;
                        color: #666;
                        margin-top: 5px;
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 20px;
                        text-align: center;
                        color: #666;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>RFID FLOW</h1>
                        <p style="margin: 10px 0 0 0;">Relatório de Cilindros</p>
                    </div>

                    <div class="content">
                        <h2 style="color: #333;">Olá!</h2>
                        <p style="color: #666; line-height: 1.6;">
                            Segue em anexo o relatório completo dos cilindros monitorados
                            pelo sistema RFID Flow, gerado em <strong>{data_hora_str}</strong>.
                        </p>

                        <div class="stats">
                            <div class="stat-card">
                                <div class="stat-value">{total_cilindros}</div>
                                <div class="stat-label">Total de Cilindros</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{total_leituras}</div>
                                <div class="stat-label">Total de Leituras RFID</div>
                            </div>
                        </div>

                        <p style="color: #666; line-height: 1.6;">
                            O arquivo Excel em anexo contém:
                        </p>
                        <ul style="color: #666; line-height: 1.8;">
                            <li>Tags RFID e números de série</li>
                            <li>Dados de fabricante</li>
                            <li>Informações de requalificação</li>
                            <li>Histórico de envasamentos (último e penúltimo)</li>
                        </ul>
                    </div>

                    <div class="footer">
                        <p><strong>RFID Flow</strong> - Rastreamento RFID de Cilindros</p>
                        <p>Este é um email automático, por favor não responda.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            email = EmailMessage(
                subject=f"Relatório RFID Flow - {data_hora_str}",
                body=corpo_html,
                from_email="RFID Flow <noreply@rfidflow.com>",
                to=[destinatario],
            )
            email.content_subtype = "html"
            email.attach(
                filename,
                excel_buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            email.send(fail_silently=False)

            messages.success(request, f"Relatório enviado para {destinatario}.")
            return redirect("dashboard")

        except Exception as e:
            messages.error(request, f"Erro ao enviar email: {str(e)}")
            return redirect("enviar_email")

    return render(request, "enviar_email.html")


# -----------------------
# Criar admin temporário (Railway)
# -----------------------

def criar_admin_temp(request):
    try:
        if not User.objects.filter(username="rfidadmin").exists():
            User.objects.create_superuser(
                username="rfidadmin",
                email="admin@rfidflow.com",
                password="RFID@Admin2024!",
            )
            return HttpResponse(
                "Superusuário criado. Username: rfidadmin | Senha: RFID@Admin2024!"
            )
        return HttpResponse("Superusuário já existe.")
    except Exception as e:
        return HttpResponse(f"Erro: {str(e)}")


# Aliases para URLs antigas
historico_busca = buscar_historico
enviar_relatorio_view = enviar_email_view


# -----------------------
# API para registrar leitura RFID
# -----------------------

@login_required
def api_registrar_leitura(request):
    if request.method != "POST":
        return JsonResponse(
        {
            "success": False,
            "error": "Método não permitido. Use POST.",
        },
        status=405,
    )

    import json

    try:
        if request.content_type == "application/json":
            data = json.loads(request.body)
            tag_rfid = data.get("tag_rfid", "").strip()
            operador = data.get("operador", "").strip()
            observacao = data.get("observacao", "").strip()
        else:
            tag_rfid = request.POST.get("tag_rfid", "").strip()
            operador = request.POST.get("operador", "").strip()
            observacao = request.POST.get("observacao", "").strip()

        if not tag_rfid:
            return JsonResponse(
                {"success": False, "error": "Tag RFID é obrigatória."},
                status=400,
            )

        botijao, criado = Botijao.objects.get_or_create(tag_rfid=tag_rfid)

        leitura = LeituraRFID.objects.create(
            botijao=botijao,
            operador=operador or None,
            observacao=observacao or None,
        )

        try:
            LogAuditoria.criar_log(
                botijao=botijao,
                acao="leitura",
                usuario=request.user if request.user.is_authenticated else None,
                descricao=f"Leitura registrada via API. Operador: {operador or '-'}; Obs: {observacao or '-'}",
                dados_anteriores=None,
                dados_novos={"leitura_id": leitura.id},
            )
        except Exception:
            pass

        return JsonResponse(
            {
                "success": True,
                "message": "Leitura registrada com sucesso.",
                "data": {
                    "botijao_id": botijao.id,
                    "tag_rfid": botijao.tag_rfid,
                    "numero_serie": botijao.numero_serie or "-",
                    "criado": criado,
                    "leitura_id": leitura.id,
                    "data_hora": leitura.data_hora.strftime("%d/%m/%Y %H:%M:%S"),
                },
            }
        )

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "error": f"Erro ao processar leitura: {str(e)}",
            },
            status=500,
        )
