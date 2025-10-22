from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone

def enviar_relatorio_email(destinatarios, arquivo_excel, assunto=None):
    """
    Envia relatório Excel por email
    
    Args:
        destinatarios: lista de emails ou string com 1 email
        arquivo_excel: caminho do arquivo .xlsx
        assunto: assunto do email (opcional)
    
    Returns:
        bool: True se enviado com sucesso
    """
    
    # Converte para lista se for string
    if isinstance(destinatarios, str):
        destinatarios = [destinatarios]
    
    # Define assunto padrão
    if not assunto:
        data = timezone.now().strftime('%d/%m/%Y')
        assunto = f'Relatório RFID - Botijões de Gás - {data}'
    
    # Corpo do email
    corpo = f"""
Olá,

Segue em anexo o relatório de rastreamento de botijões RFID.

📊 Informações do relatório:
- Gerado em: {timezone.now().strftime('%d/%m/%Y às %H:%M')}
- Sistema: Rastreamento RFID de Botijões

Este é um email automático. Por favor, não responda.

Atenciosamente,
Sistema de Rastreamento RFID
    """.strip()
    
    try:
        # Cria email
        email = EmailMessage(
            subject=assunto,
            body=corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
        )
        
        # Anexa arquivo Excel
        email.attach_file(arquivo_excel)
        
        # Envia
        email.send(fail_silently=False)
        
        print(f"✅ Email enviado para: {', '.join(destinatarios)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False