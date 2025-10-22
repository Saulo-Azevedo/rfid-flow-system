from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt  # ⬅️ ADICIONE ESTA LINHA
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from .utils.audit_log import registrar_leitura_rfid

from .models import Botijao, Leitura, ConfiguracaoSistema
from .forms import NovaLeituraForm, FiltroRelatorioForm
from .utils.export_excel import gerar_excel_botijoes, gerar_excel_leituras
from .utils.send_email import enviar_relatorio_email

def get_botijoes_ativos():
    """Retorna apenas botijões não deletados"""
    return Botijao.objects.filter(deletado=False)

@login_required
def dashboard(request):
    """Dashboard principal com estatísticas"""
    
    # Estatísticas (apenas botijões não deletados)
    total_botijoes = Botijao.objects.filter(deletado=False).count()
    botijoes_ativos = Botijao.objects.filter(deletado=False, status='ativo').count()
    
    # Leituras hoje
    hoje = timezone.now().date()
    leituras_hoje = Leitura.objects.filter(data_hora__date=hoje).count()
    
    # Última leitura
    ultima = Leitura.objects.order_by('-data_hora').first()
    ultima_leitura = ultima.data_hora.strftime('%H:%M') if ultima else None
    
    # Lista de botijões (últimos 50, apenas não deletados)
    botijoes = Botijao.objects.filter(deletado=False).order_by('-data_cadastro')[:50]
    
    context = {
        'total_botijoes': total_botijoes,
        'botijoes_ativos': botijoes_ativos,
        'leituras_hoje': leituras_hoje,
        'ultima_leitura': ultima_leitura,
        'botijoes': botijoes,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def nova_leitura(request):
    """Formulário para registrar nova leitura manual"""
    
    if request.method == 'POST':
        form = NovaLeituraForm(request.POST)
        
        if form.is_valid():
            tag_rfid = form.cleaned_data['tag_rfid']
            operador = form.cleaned_data['operador']
            observacao = form.cleaned_data['observacao']
            localizacao = form.cleaned_data.get('localizacao', '')
            numero_serie = form.cleaned_data.get('numero_serie', '')
            
            # Busca ou cria botijão
            botijao, criado = Botijao.objects.get_or_create(
                tag_rfid=tag_rfid,
                defaults={
                    'numero_serie': numero_serie,  # Será gerado auto se vazio
                }
            )
            
            # Registra leitura com localização
            botijao.registrar_leitura(
                operador=operador,
                observacao=observacao,
                localizacao=localizacao,
                request=request
            )
            
            if criado:
                messages.success(request, f'✅ Novo botijão cadastrado e leitura registrada! Tag: {tag_rfid} | Nº Série: {botijao.numero_serie}')
            else:
                messages.success(request, f'✅ Leitura registrada com sucesso! Tag: {tag_rfid}')
            
            return redirect('dashboard')
    else:
        form = NovaLeituraForm()
    
    return render(request, 'nova_leitura.html', {'form': form})

@login_required
def historico_botijao(request, botijao_id):
    """Visualiza histórico de um botijão específico (via ID direto)"""
    
    botijao = get_object_or_404(Botijao, id=botijao_id)
    
    # Filtros opcionais de data
    leituras = botijao.historico.all()
    
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if data_inicio:
        leituras = leituras.filter(data_hora__date__gte=data_inicio)
    if data_fim:
        leituras = leituras.filter(data_hora__date__lte=data_fim)
    
    context = {
        'botijao': botijao,
        'leituras': leituras,
    }
    
    return render(request, 'historico_botijao.html', context)

@login_required
def historico_busca(request):
    """Página de busca de histórico por Tag ou Série"""
    
    botijao = None
    leituras = Leitura.objects.none()
    
    tag_rfid = request.GET.get('tag_rfid', '').strip()
    numero_serie = request.GET.get('numero_serie', '').strip()
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Busca por Tag
    if tag_rfid:
        try:
            botijao = Botijao.objects.get(tag_rfid__icontains=tag_rfid)
            leituras = botijao.historico.all()
        except Botijao.DoesNotExist:
            messages.error(request, f'❌ Nenhum botijão encontrado com a tag "{tag_rfid}"')
    
    # Busca por Número de Série
    elif numero_serie:
        try:
            botijao = Botijao.objects.get(numero_serie__icontains=numero_serie)
            leituras = botijao.historico.all()
        except Botijao.DoesNotExist:
            messages.error(request, f'❌ Nenhum botijão encontrado com o número de série "{numero_serie}"')
    
    # Filtrar por data se fornecido
    if leituras.exists():
        if data_inicio:
            leituras = leituras.filter(data_hora__date__gte=data_inicio)
        if data_fim:
            leituras = leituras.filter(data_hora__date__lte=data_fim)
    
    context = {
        'botijao': botijao,
        'leituras': leituras,
    }
    
    return render(request, 'historico_botijao.html', context)

@login_required
def relatorios(request):
    """Página de relatórios com filtros"""
    
    form = FiltroRelatorioForm(request.GET or None)
    
    # Aplica filtros
    botijoes = Botijao.objects.all()
    
    if form.is_valid():
        status = form.cleaned_data.get('status')
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        
        if status:
            botijoes = botijoes.filter(status=status)
        
        if data_inicio:
            botijoes = botijoes.filter(ultima_leitura__gte=data_inicio)
        
        if data_fim:
            botijoes = botijoes.filter(ultima_leitura__lte=data_fim)
    
    # Estatísticas do filtro
    total_filtrado = botijoes.count()
    total_leituras = sum(b.total_leituras for b in botijoes)
    
    context = {
        'form': form,
        'botijoes': botijoes,
        'total_filtrado': total_filtrado,
        'total_leituras': total_leituras,
    }
    
    return render(request, 'relatorios.html', context)


def exportar_excel(request):
    """Exporta relatório em Excel"""
    
    tipo = request.GET.get('tipo', 'botijoes')
    
    try:
        if tipo == 'botijoes':
            filepath = gerar_excel_botijoes()
            filename = f'relatorio_botijoes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        else:
            filepath = gerar_excel_leituras()
            filename = f'relatorio_leituras_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        # Lê arquivo e retorna como download
        with open(filepath, 'rb') as f:
            response = HttpResponse(
                f.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
        messages.success(request, '✅ Excel gerado com sucesso!')
        return response
        
    except Exception as e:
        messages.error(request, f'❌ Erro ao gerar Excel: {str(e)}')
        return redirect('dashboard')

@login_required
def enviar_relatorio_view(request):
    """Envia relatório por email"""
    
    if request.method == 'POST':
        email_destino = request.POST.get('email')
        
        if not email_destino:
            messages.error(request, '❌ Informe um email válido')
            return redirect('dashboard')
        
        try:
            # Gera Excel
            filepath = gerar_excel_botijoes()
            
            # Envia por email
            sucesso = enviar_relatorio_email(
                destinatarios=email_destino,
                arquivo_excel=filepath
            )
            
            if sucesso:
                messages.success(request, f'✅ Relatório enviado para {email_destino}')
            else:
                messages.error(request, '❌ Erro ao enviar email')
                
        except Exception as e:
            messages.error(request, f'❌ Erro: {str(e)}')
        
        return redirect('dashboard')
    
    # GET - mostra formulário
    config = ConfiguracaoSistema.get_config()
    return render(request, 'enviar_relatorio.html', {
        'email_padrao': config.email_relatorios
    })

@csrf_exempt
def api_registrar_leitura(request):
    """API simples para registrar leitura via POST"""
    
    if request.method == 'POST':
        import json
        
        try:
            data = json.loads(request.body)
            tag_rfid = data.get('tag_rfid')
            operador = data.get('operador', '')
            observacao = data.get('observacao', '')
            localizacao = data.get('localizacao', '')
            
            if not tag_rfid:
                return JsonResponse({'erro': 'tag_rfid obrigatório'}, status=400)
            
            # Busca ou cria botijão
            botijao, criado = Botijao.objects.get_or_create(
                tag_rfid=tag_rfid
            )
            
            # Registra leitura com localização
            leitura = botijao.registrar_leitura(
                operador=operador,
                observacao=observacao,
                localizacao=localizacao,
                request=request
            )
            
            return JsonResponse({
                'sucesso': True,
                'botijao_id': botijao.id,
                'leitura_id': leitura.id,
                'novo': criado,
                'numero_serie': botijao.numero_serie,
                'total_leituras': botijao.total_leituras
            })
            
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=500)
        

@login_required
def dashboard_api(request):
    """API que retorna dados atualizados do dashboard em JSON"""
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Estatísticas
    total_botijoes = Botijao.objects.filter(deletado=False).count()
    botijoes_ativos = Botijao.objects.filter(deletado=False, status='ativo').count()
    
    # Leituras de hoje
    hoje = timezone.now().date()
    leituras_hoje = Leitura.objects.filter(data_hora__date=hoje).count()
    
    # Última leitura
    ultima = Leitura.objects.order_by('-data_hora').first()
    ultima_leitura = ultima.data_hora.strftime('%H:%M') if ultima else '--:--'
    
    # Últimos 10 botijões
    botijoes = Botijao.objects.filter(deletado=False).select_related().order_by('-id')[:10]
    
    botijoes_data = []
    for b in botijoes:
        botijoes_data.append({
            'id': b.id,
            'tag_rfid': b.tag_rfid[:25],
            'numero_serie': b.numero_serie or '-',
            'cliente': b.cliente or '-',
            'localizacao': b.localizacao or '-',
            'status': b.status,
            'status_display': b.get_status_display(),
            'total_leituras': b.leituras.count(),
            'ultima_leitura': b.ultima_leitura.strftime('%d/%m/%Y %H:%M') if b.ultima_leitura else '-',
        })
    
    return JsonResponse({
        'total_botijoes': total_botijoes,
        'leituras_hoje': leituras_hoje,
        'ultima_leitura': ultima_leitura,
        'botijoes_ativos': botijoes_ativos,
        'botijoes': botijoes_data,
    })


@login_required
def relatorios_api(request):
    """API que retorna dados atualizados dos relatórios em JSON"""
    
    # Pega os filtros da URL
    status = request.GET.get('status', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    # Filtra botijões
    botijoes = Botijao.objects.filter(deletado=False)
    
    if status:
        botijoes = botijoes.filter(status=status)
    
    if data_inicio:
        botijoes = botijoes.filter(criado_em__gte=data_inicio)
    
    if data_fim:
        botijoes = botijoes.filter(criado_em__lte=data_fim)
    
    # Estatísticas
    total_filtrado = botijoes.count()
    total_leituras = sum(b.leituras.count() for b in botijoes)
    
    # Lista de botijões
    botijoes_data = []
    for b in botijoes[:50]:  # Limita a 50 para performance
        botijoes_data.append({
            'tag_rfid': b.tag_rfid[:20],
            'numero_serie': b.numero_serie or '-',
            'status': b.status,
            'status_display': b.get_status_display(),
            'total_leituras': b.leituras.count(),
            'ultima_leitura': b.ultima_leitura.strftime('%d/%m/%Y %H:%M') if b.ultima_leitura else '-',
            'capacidade': b.capacidade or '-',
            'cliente': b.cliente or '-',
        })
    
    return JsonResponse({
        'total_filtrado': total_filtrado,
        'total_leituras': total_leituras,
        'botijoes': botijoes_data,
    })        
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


from django.contrib.auth.models import User
from django.http import HttpResponse

def criar_admin_temp(request):
    """View temporária para criar superusuário"""
    username = 'rfidadmin'  # ⬅️ NOME DIFERENTE
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email='admin@rfidflow.com',
            password='RFID@Admin2024!'
        )
        return HttpResponse(f'''
            <h1>✅ Superusuário criado com sucesso!</h1>
            <p><strong>Username:</strong> {username}</p>
            <p><strong>Password:</strong> RFID@Admin2024!</p>
            <br>
            <a href="/admin/" style="padding: 10px 20px; background: #00D4FF; color: white; text-decoration: none; border-radius: 5px;">Ir para Admin</a>
            <br><br>
            <a href="/" style="padding: 10px 20px; background: #00E676; color: white; text-decoration: none; border-radius: 5px;">Ir para Login</a>
        ''')
    return HttpResponse(f'''
        <h1>⚠️ Usuário {username} já existe!</h1>
        <p>Tente fazer login com as credenciais anteriores</p>
        <br>
        <a href="/admin/" style="padding: 10px 20px; background: #00D4FF; color: white; text-decoration: none; border-radius: 5px;">Ir para Admin</a>
    ''')