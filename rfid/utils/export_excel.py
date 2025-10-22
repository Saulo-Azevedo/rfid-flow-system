import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.utils import timezone
from django.conf import settings
import os

def gerar_excel_botijoes(filepath=None):
    """
    Gera planilha Excel com todos os botijões
    """
    from rfid.models import Botijao
    
    if not filepath:
        # Cria diretório temporário se não existir
        temp_dir = os.path.join(settings.BASE_DIR, 'temp_exports')
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(temp_dir, f'relatorio_botijoes_{timestamp}.xlsx')
    
    # Cria workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Botijões"
    
    # Estilos
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Cabeçalhos
    headers = [
        'Tag RFID', 'Nº Série', 'Cliente', 'Localização', 
        'Status', 'Total Leituras', 'Data Cadastro', 
        'Última Leitura', 'Capacidade', 'Observações'
    ]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(1, col, header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border
    
    # Dados
    botijoes = Botijao.objects.filter(deletado=False).order_by('-data_cadastro')
    
    for row, botijao in enumerate(botijoes, 2):
        ws.cell(row, 1, botijao.tag_rfid).border = border
        ws.cell(row, 2, botijao.numero_serie or '-').border = border
        ws.cell(row, 3, botijao.cliente or '-').border = border
        ws.cell(row, 4, botijao.localizacao or '-').border = border
        ws.cell(row, 5, botijao.get_status_display()).border = border
        ws.cell(row, 6, botijao.leituras.count()).border = border
        
        if botijao.data_cadastro:
            ws.cell(row, 7, botijao.data_cadastro.strftime('%d/%m/%Y %H:%M')).border = border
        else:
            ws.cell(row, 7, '-').border = border
        
        if botijao.ultima_leitura:
            ws.cell(row, 8, botijao.ultima_leitura.strftime('%d/%m/%Y %H:%M')).border = border
        else:
            ws.cell(row, 8, '-').border = border
        
        ws.cell(row, 9, str(botijao.capacidade)).border = border
        ws.cell(row, 10, botijao.observacao or '-').border = border

    # Ajusta largura das colunas
    column_widths = [25, 20, 25, 25, 12, 15, 18, 18, 12, 40]
    
    # Congela primeira linha
    ws.freeze_panes = 'A2'
    
    # Salva
    wb.save(filepath)
    print(f"✅ Excel de botijões gerado: {filepath}")
    return filepath


def gerar_excel_leituras(data_inicio=None, data_fim=None, filepath=None):
    """
    Gera planilha Excel com histórico de leituras
    """
    from rfid.models import Leitura
    
    if not filepath:
        temp_dir = os.path.join(settings.BASE_DIR, 'temp_exports')
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(temp_dir, f'relatorio_leituras_{timestamp}.xlsx')
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leituras"
    
    # Estilos
    header_fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Cabeçalhos
    headers = ['Data/Hora', 'Tag RFID', 'Nº Série', 'Cliente', 'Operador', 'Localização', 'Observação']
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(1, col, header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border
    
    # Filtra leituras
    leituras = Leitura.objects.select_related('botijao').all()
    
    if data_inicio:
        leituras = leituras.filter(data_hora__gte=data_inicio)
    if data_fim:
        leituras = leituras.filter(data_hora__lte=data_fim)
    
    # Dados
    for row, leitura in enumerate(leituras, 2):
        ws.cell(row, 1, leitura.data_hora.strftime('%d/%m/%Y %H:%M:%S')).border = border
        ws.cell(row, 2, leitura.tag_rfid).border = border
        ws.cell(row, 3, leitura.botijao.numero_serie if leitura.botijao and leitura.botijao.numero_serie else '-').border = border
        ws.cell(row, 4, leitura.botijao.cliente if leitura.botijao and leitura.botijao.cliente else '-').border = border
        ws.cell(row, 5, leitura.operador or '-').border = border
        ws.cell(row, 6, leitura.localizacao or '-').border = border
        ws.cell(row, 7, leitura.observacao or '-').border = border

    # Ajusta larguras
    column_widths = [20, 25, 20, 25, 20, 25, 40]
    
    ws.freeze_panes = 'A2'
    
    wb.save(filepath)
    print(f"✅ Excel de leituras gerado: {filepath}")
    return filepath