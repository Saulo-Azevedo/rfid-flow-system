# rfid/views.py - VIEWS SUPER OTIMIZADAS ⚡
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.models import User
from datetime import timedelta, date
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from .models import Botijao, LeituraRFID, LogAuditoria
# ... outras importações
from .forms import FiltroRelatorioForm

# ========== DASHBOARD ==========
@login_required
def dashboard(request):
    """Dashboard principal com estatísticas - OTIMIZADO"""
    
    hoje = timezone.now().date()
    
    # Estatísticas
    total_botijoes = Botijao.objects.count()
    botijoes_ativos = Botijao.objects.filter(status='ativo').count()
    leituras_hoje = LeituraRFID.objects.filter(data_hora__date=hoje).count()
    
    # Última leitura
    ultima_leitura_obj = LeituraRFID.objects.order_by('-data_hora').first()
    ultima_leitura = ultima_leitura_obj.data_hora.strftime('%H:%M') if ultima_leitura_obj else '--:--'
    
    # ⚡ OTIMIZADO: Últimos botijões com annotate (sem conflito)
    botijoes = Botijao.objects.annotate(
        num_leituras=Count('leituras')  # ✅ Nome diferente da property
    ).order_by('-data_cadastro')[:10]
    
    # Leituras dos últimos 7 dias (para gráfico)
    leituras_7_dias = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        count = LeituraRFID.objects.filter(data_hora__date=dia).count()
        leituras_7_dias.append({
            'data': dia.strftime('%d/%m'),
            'total': count
        })
    
    # Status dos botijões (para gráfico)
    status_counts = Botijao.objects.values('status').annotate(
        total=Count('id')
    )
    
    context = {
        'total_botijoes': total_botijoes,
        'botijoes_ativos': botijoes_ativos,
        'leituras_hoje': leituras_hoje,
        'ultima_leitura': ultima_leitura,
        'botijoes': botijoes,
        'leituras_7_dias': leituras_7_dias,
        'status_counts': status_counts,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def dashboard_api(request):
    """API para atualização AJAX do dashboard - OTIMIZADA"""
    
    hoje = timezone.now().date()
    
    # Estatísticas
    total_botijoes = Botijao.objects.count()
    botijoes_ativos = Botijao.objects.filter(status='ativo').count()
    leituras_hoje = LeituraRFID.objects.filter(data_hora__date=hoje).count()
    
    # Última leitura
    ultima_leitura_obj = LeituraRFID.objects.order_by('-data_hora').first()
    ultima_leitura = ultima_leitura_obj.data_hora.strftime('%H:%M') if ultima_leitura_obj else '--:--'
    
    # ⚡ OTIMIZADO: Últimos botijões com annotate
    botijoes = Botijao.objects.annotate(
        num_leituras=Count('leituras')  # ✅ Nome diferente
    ).order_by('-data_cadastro')[:10]
    
    botijoes_data = []
    for b in botijoes:
        # Usa a property ultima_leitura do modelo
        ultima = b.ultima_leitura
        
        botijoes_data.append({
            'id': b.id,
            'tag_rfid': b.tag_rfid,
            'numero_serie': b.numero_serie or '-',
            'fabricante': b.fabricante or '-',
            'cliente': b.cliente or '-',
            'localizacao': b.localizacao or '-',
            'status': b.status,
            'status_display': b.get_status_display(),
            'status_requalificacao': b.status_requalificacao,
            'status_requalificacao_display': b.get_status_requalificacao_display(),
            'total_leituras': b.num_leituras,  # ✅ Usa o annotate
            'ultima_leitura': ultima.strftime('%d/%m/%Y %H:%M') if ultima else '-'
        })
    
    # Leituras dos últimos 7 dias
    leituras_7_dias = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        count = LeituraRFID.objects.filter(data_hora__date=dia).count()
        leituras_7_dias.append({
            'data': dia.strftime('%d/%m'),
            'total': count
        })
    
    # Status dos botijões
    status_counts = []
    for status_choice in Botijao.STATUS_CHOICES:
        count = Botijao.objects.filter(status=status_choice[0]).count()
        status_counts.append({
            'status': status_choice[1],
            'total': count
        })
    
    return JsonResponse({
        'total_botijoes': total_botijoes,
        'botijoes_ativos': botijoes_ativos,
        'leituras_hoje': leituras_hoje,
        'ultima_leitura': ultima_leitura,
        'botijoes': botijoes_data,
        'leituras_7_dias': leituras_7_dias,
        'status_counts': status_counts,
    })


# ========== NOVA LEITURA ==========
@login_required
def nova_leitura(request):
    """Registra uma nova leitura RFID"""
    
    if request.method == 'POST':
        tag_rfid = request.POST.get('tag_rfid', '').strip()
        operador = request.POST.get('operador', '').strip()
        observacao = request.POST.get('observacao', '').strip()
        
        if not tag_rfid:
            messages.error(request, 'Tag RFID é obrigatória!')
            return redirect('nova_leitura')
        
        # Busca ou cria o botijão
        botijao, criado = Botijao.objects.get_or_create(tag_rfid=tag_rfid)
        
        # Registra a leitura
        LeituraRFID.objects.create(
            botijao=botijao,
            operador=operador,
            observacao=observacao
        )
        
        if criado:
            messages.success(request, f'✅ Novo botijão cadastrado e leitura registrada! Tag: {tag_rfid}')
        else:
            messages.success(request, f'✅ Leitura registrada! Tag: {tag_rfid}')
        
        return redirect('dashboard')
    
    return render(request, 'nova_leitura.html')


# ========== RELATÓRIOS ==========
@login_required
def relatorios(request):
    """Página de relatórios com filtros - SUPER OTIMIZADA"""
    # 1. Instanciar o formulário com os dados da requisição GET
    # Isso preenche os campos do formulário com os valores que o usuário digitou
    form = FiltroRelatorioForm(request.GET)
    
    # Filtros
    status = request.GET.get('status', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    # Query base com annotate OTIMIZADO
    botijoes = Botijao.objects.annotate(
        num_leituras=Count('leituras')  # ✅ Nome diferente da property
    )
    
    # Aplicar filtros
    if status:
        botijoes = botijoes.filter(status=status)
    
    if data_inicio:
        botijoes = botijoes.filter(data_cadastro__gte=data_inicio)
    
    if data_fim:
        botijoes = botijoes.filter(data_cadastro__lte=data_fim)
    
    # ⚡ OTIMIZADO: Order by primeiro
    botijoes = botijoes.order_by('-data_cadastro')
    
    # Preparar dados para template
    botijoes_data = []
    for b in botijoes:
        # Usa a property ultima_leitura do modelo (mais simples)
        ultima = b.ultima_leitura
        
        botijoes_data.append({
            'id': b.id,
            'tag_rfid': b.tag_rfid,
            'numero_serie': b.numero_serie or '-',
            'fabricante': b.fabricante or '-',
            'status': b.status,
            'status_display': b.get_status_display(),
            'status_requalificacao': b.status_requalificacao,
            'status_requalificacao_display': b.get_status_requalificacao_display(),
            'total_leituras': b.num_leituras,  # ✅ Usa o annotate
            'ultima_leitura': ultima.strftime('%d/%m/%Y %H:%M') if ultima else '-',
            'capacidade': b.capacidade or '-',
            'cliente': b.cliente or '-',
        })
    
    context = {
        'botijoes': botijoes_data,
        'total_filtrado': botijoes.count(),
        'total_leituras': LeituraRFID.objects.count(),
        'status_filter': status,
        'data_inicio_filter': data_inicio,
        'data_fim_filter': data_fim,
        'form': form,
    }
    
    return render(request, 'relatorios.html', context)


@login_required
def relatorios_api(request):
    """API para atualização AJAX dos relatórios - SUPER OTIMIZADA"""
    
    # Filtros
    status = request.GET.get('status', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    # Query base com annotate OTIMIZADO
    botijoes = Botijao.objects.annotate(
        num_leituras=Count('leituras')  # ✅ Nome diferente
    )
    
    # Aplicar filtros
    if status:
        botijoes = botijoes.filter(status=status)
    
    if data_inicio:
        botijoes = botijoes.filter(data_cadastro__gte=data_inicio)
    
    if data_fim:
        botijoes = botijoes.filter(data_cadastro__lte=data_fim)
    
    # ⚡ OTIMIZADO: Order by
    botijoes = botijoes.order_by('-data_cadastro')
    
    # Preparar dados
    botijoes_data = []
    for b in botijoes:
        # Usa a property ultima_leitura do modelo
        ultima = b.ultima_leitura
        
        botijoes_data.append({
            'tag_rfid': b.tag_rfid,
            'numero_serie': b.numero_serie or '-',
            'fabricante': b.fabricante or '-',
            'status': b.status,
            'status_display': b.get_status_display(),
            'status_requalificacao': b.status_requalificacao,
            'total_leituras': b.num_leituras,  # ✅ Usa o annotate
            'ultima_leitura': ultima.strftime('%d/%m/%Y %H:%M') if ultima else '-',
            'capacidade': str(b.capacidade) if b.capacidade else '-',
            'cliente': b.cliente or '-',
        })
    
    return JsonResponse({
        'botijoes': botijoes_data,
        'total_filtrado': botijoes.count(),
        'total_leituras': LeituraRFID.objects.count(),
    })


# ========== EXPORTAR EXCEL ==========
@login_required
def exportar_excel(request):
    """Exporta relatório de botijões para Excel - OTIMIZADO"""
    
    # Criar workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Botijões RFID"
    
    # Cabeçalhos
    headers = [
        'Tag RFID', 'Nº Série', 'Fabricante', 'Status', 
        'Status Requalificação', 'Cliente', 'Localização',
        'Capacidade (kg)', 'Tara (kg)', 'Total Leituras',
        'Última Leitura', 'Data Cadastro'
    ]
    
    ws.append(headers)
    
    # Estilizar cabeçalho
    header_fill = PatternFill(start_color="00D4FF", end_color="00D4FF", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # ⚡ OTIMIZADO: Annotate
    botijoes = Botijao.objects.annotate(
        num_leituras=Count('leituras')
    ).order_by('-data_cadastro')
    
    # Dados
    for b in botijoes:
        # Usa a property ultima_leitura do modelo
        ultima = b.ultima_leitura
        
        ws.append([
            b.tag_rfid,
            b.numero_serie or '-',
            b.fabricante or '-',
            b.get_status_display(),
            b.get_status_requalificacao_display(),
            b.cliente or '-',
            b.localizacao or '-',
            float(b.capacidade) if b.capacidade else '-',
            float(b.tara) if b.tara else '-',
            b.num_leituras,  # ✅ Usa o annotate
            ultima.strftime('%d/%m/%Y %H:%M') if ultima else '-',
            b.data_cadastro.strftime('%d/%m/%Y %H:%M')
        ])
    
    # Ajustar largura das colunas
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Preparar response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'relatorio_rfid_flow_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb.save(response)
    return response


# ========== HISTÓRICO BOTIJÃO ==========
@login_required
def historico_botijao(request, botijao_id):
    """Exibe histórico completo de um botijão - OTIMIZADO"""
    
    # ⚡ OTIMIZADO: select_related para evitar queries extras
    botijao = get_object_or_404(
        Botijao.objects.annotate(num_leituras=Count('leituras')),
        id=botijao_id
    )
    
    # Leituras já ordenadas
    leituras = LeituraRFID.objects.filter(botijao=botijao).order_by('-data_hora')
    
    context = {
        'botijao': botijao,
        'leituras': leituras,
    }
    
    return render(request, 'historico_botijao.html', context)

# ========== BUSCAR HISTÓRICO ==========
# rfid/views.py

@login_required
def buscar_historico(request):
    """Busca histórico de leituras por Tag RFID ou Número de Série"""
    
    query = request.GET.get('q', '').strip()
    
    resultados = []
    
    if query:
        # Busca por tag_rfid ou numero_serie
        botijoes = Botijao.objects.filter(
            Q(tag_rfid__icontains=query) | 
            Q(numero_serie__icontains=query)
        ).annotate(
            num_leituras=Count('leituras')
        ).prefetch_related('leituras')
        
        for b in botijoes:
            # Pega as 10 últimas leituras
            leituras = list(b.leituras.order_by('-data_hora')[:10])
            
            leituras_data = []
            for l in leituras:
                leituras_data.append({
                    'data_hora': l.data_hora.strftime('%d/%m/%Y %H:%M:%S'),
                    'operador': l.operador or '-',
                    'observacao': l.observacao or '-',
                })
            
            resultados.append({
                'botijao': {
                    'id': b.id,
                    'tag_rfid': b.tag_rfid,
                    'numero_serie': b.numero_serie or '-',
                    'fabricante': b.fabricante or '-',
                    'status': b.status,
                    'status_display': b.get_status_display(),
                    'cliente': b.cliente or '-',
                    'localizacao': b.localizacao or '-',
                },
                'leituras': leituras_data,
                'total_leituras': b.num_leituras,
            })
    
    context = {
        'query': query,
        'resultados': resultados,
        'total_encontrados': len(resultados),
    }
    
    # ✅ CORRIGIDO - Renderiza template de BUSCA
    return render(request, 'historico_busca.html', context)

# ========== ENVIAR EMAIL ==========
@login_required
def enviar_email_view(request):
    """Envia relatório de botijões por email com Excel anexado"""
    
    if request.method == 'POST':
        destinatario = request.POST.get('destinatario', '').strip()
        
        if not destinatario:
            messages.error(request, 'Email de destinatário é obrigatório!')
            return redirect('enviar_email')
        
        try:
            # ========== GERAR EXCEL EM MEMÓRIA ==========
            from io import BytesIO
            from django.core.mail import EmailMessage
            
            # Criar workbook em memória
            wb = Workbook()
            ws = wb.active
            ws.title = "Botijões RFID"
            
            # Cabeçalhos
            headers = [
                'Tag RFID', 'Nº Série', 'Fabricante', 'Status', 
                'Status Requalificação', 'Cliente', 'Localização',
                'Capacidade (kg)', 'Tara (kg)', 'Total Leituras',
                'Última Leitura', 'Data Cadastro'
            ]
            ws.append(headers)
            
            # Estilizar cabeçalho
            header_fill = PatternFill(start_color="00D4FF", end_color="00D4FF", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Buscar dados otimizados
            botijoes = Botijao.objects.annotate(
                num_leituras=Count('leituras')
            ).order_by('-data_cadastro')
            
            # Adicionar dados
            for b in botijoes:
                ultima = b.ultima_leitura
                ws.append([
                    b.tag_rfid,
                    b.numero_serie or '-',
                    b.fabricante or '-',
                    b.get_status_display(),
                    b.get_status_requalificacao_display(),
                    b.cliente or '-',
                    b.localizacao or '-',
                    float(b.capacidade) if b.capacidade else '-',
                    float(b.tara) if b.tara else '-',
                    b.num_leituras,
                    ultima.strftime('%d/%m/%Y %H:%M') if ultima else '-',
                    b.data_cadastro.strftime('%d/%m/%Y %H:%M')
                ])
            
            # Ajustar largura das colunas
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # Salvar em BytesIO
            excel_buffer = BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)
            
            # ========== PREPARAR E ENVIAR EMAIL ==========
            data_hora = timezone.now().strftime('%d/%m/%Y às %H:%M')
            filename = f'relatorio_rfid_flow_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            
            # Estatísticas para o corpo do email
            total_botijoes = botijoes.count()
            botijoes_ativos = botijoes.filter(status='ativo').count()
            total_leituras = LeituraRFID.objects.count()
            
            # Corpo do email em HTML
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
                    .btn {{
                        display: inline-block;
                        padding: 12px 30px;
                        background: #00D4FF;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 RFID FLOW</h1>
                        <p style="margin: 10px 0 0 0;">Relatório de Botijões de Gás</p>
                    </div>
                    
                    <div class="content">
                        <h2 style="color: #333;">Olá!</h2>
                        <p style="color: #666; line-height: 1.6;">
                            Segue em anexo o relatório completo do sistema RFID Flow 
                            gerado em <strong>{data_hora}</strong>.
                        </p>
                        
                        <div class="stats">
                            <div class="stat-card">
                                <div class="stat-value">{total_botijoes}</div>
                                <div class="stat-label">Total de Botijões</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{botijoes_ativos}</div>
                                <div class="stat-label">Botijões Ativos</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">{total_leituras}</div>
                                <div class="stat-label">Total de Leituras</div>
                            </div>
                        </div>
                        
                        <p style="color: #666; line-height: 1.6;">
                            O arquivo Excel anexo contém informações detalhadas sobre:
                        </p>
                        <ul style="color: #666; line-height: 1.8;">
                            <li>Tags RFID e números de série</li>
                            <li>Informações de fabricantes</li>
                            <li>Status de cada botijão</li>
                            <li>Status de requalificação</li>
                            <li>Dados de clientes e localização</li>
                            <li>Histórico de leituras</li>
                        </ul>
                    </div>
                    
                    <div class="footer">
                        <p><strong>RFID Flow</strong> - Sistema de Rastreamento RFID</p>
                        <p>Este é um email automático, não responda.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Criar email
            email = EmailMessage(
                subject=f'Relatório RFID Flow - {data_hora}',
                body=corpo_html,
                from_email='RFID Flow <noreply@rfidflow.com>',
                to=[destinatario],
            )
            
            # Definir como HTML
            email.content_subtype = "html"
            
            # Anexar Excel
            email.attach(filename, excel_buffer.getvalue(), 
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            
            # Enviar
            email.send(fail_silently=False)
            
            messages.success(request, f'✅ Relatório enviado com sucesso para {destinatario}!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'❌ Erro ao enviar email: {str(e)}')
            return redirect('enviar_relatorio')
    
    return render(request, 'enviar_email.html')


# ========== CRIAR ADMIN TEMPORÁRIO (Apenas para Railway) ==========
def criar_admin_temp(request):
    """View temporária para criar superusuário na Railway"""
    
    # ATENÇÃO: REMOVER ESTA VIEW EM PRODUÇÃO!
    # Esta view é apenas para facilitar a criação do primeiro admin
    
    try:
        if not User.objects.filter(username='rfidadmin').exists():
            User.objects.create_superuser(
                username='rfidadmin',
                email='admin@rfidflow.com',
                password='RFID@Admin2024!'
            )
            return HttpResponse('✅ Superusuário criado! Username: rfidadmin | Senha: RFID@Admin2024!')
        else:
            return HttpResponse('ℹ️ Superusuário já existe!')
    except Exception as e:
        return HttpResponse(f'❌ Erro: {str(e)}')


# ========== ALIASES PARA COMPATIBILIDADE COM URLS ANTIGAS ==========
# Alias para manter compatibilidade com nome antigo
historico_busca = buscar_historico

# Alias para manter compatibilidade com nome antigo
enviar_relatorio_view = enviar_email_view


# ========== API REGISTRAR LEITURA RFID ==========
@login_required
def api_registrar_leitura(request):
    """
    API para registrar leitura RFID via POST
    POST /api/registrar-leitura/
    
    Parâmetros:
    - tag_rfid: Tag RFID lida (obrigatório)
    - operador: Nome do operador (opcional)
    - observacao: Observações (opcional)
    """
    
    if request.method == 'POST':
        try:
            import json
            
            # Tenta pegar do POST ou do JSON body
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                tag_rfid = data.get('tag_rfid', '').strip()
                operador = data.get('operador', '').strip()
                observacao = data.get('observacao', '').strip()
            else:
                tag_rfid = request.POST.get('tag_rfid', '').strip()
                operador = request.POST.get('operador', '').strip()
                observacao = request.POST.get('observacao', '').strip()
            
            if not tag_rfid:
                return JsonResponse({
                    'success': False,
                    'error': 'Tag RFID é obrigatória!'
                }, status=400)
            
            # Busca ou cria o botijão
            botijao, criado = Botijao.objects.get_or_create(tag_rfid=tag_rfid)
            
            # Registra a leitura
            leitura = LeituraRFID.objects.create(
                botijao=botijao,
                operador=operador,
                observacao=observacao
            )
            
            # Registra no log de auditoria
            try:
                LogAuditoria.criar_log(
                    botijao=botijao,
                    acao='leitura',
                    usuario=operador or 'Sistema',
                    descricao=f'Leitura RFID registrada via API. {observacao}'
                )
            except:
                pass  # Se falhar o log, não quebra a leitura
            
            # ⚡ OTIMIZADO: Conta leituras com annotate
            botijao_com_contagem = Botijao.objects.annotate(
                num_leituras=Count('leituras')
            ).get(id=botijao.id)
            
            return JsonResponse({
                'success': True,
                'message': 'Leitura registrada com sucesso!',
                'data': {
                    'botijao_id': botijao.id,
                    'tag_rfid': botijao.tag_rfid,
                    'numero_serie': botijao.numero_serie or '-',
                    'criado': criado,
                    'leitura_id': leitura.id,
                    'data_hora': leitura.data_hora.strftime('%d/%m/%Y %H:%M:%S'),
                    'total_leituras': botijao_com_contagem.num_leituras,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao processar leitura: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Método não permitido. Use POST.'
    }, status=405)