import logging
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger("rfid")


def enviar_relatorio_email(destinatarios, arquivo_excel, assunto=None):
    """
    Envia relatório Excel por email usando SendGrid (API via Anymail).

    Args:
        destinatarios (list[str] | str): emails de destino
        arquivo_excel (str): caminho do arquivo .xlsx
        assunto (str | None): assunto do email

    Returns:
        bool: True se enviado com sucesso, False se erro
    """

    # Normaliza destinatários
    if isinstance(destinatarios, str):
        destinatarios = [destinatarios]

    # Assunto padrão
    if not assunto:
        data = timezone.now().strftime("%d/%m/%Y")
        assunto = f"Relatório RFID - Botijões de Gás - {data}"

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
        # FROM: obtém DEFAULT_FROM_EMAIL e sanitiza
        raw_from = (getattr(settings, "DEFAULT_FROM_EMAIL", "") or "").strip()
        safe_from = raw_from

        # Remove "Nome <email@dominio>" se existir
        if "<" in safe_from and ">" in safe_from:
            safe_from = safe_from.split("<", 1)[1].split(">", 1)[0].strip()

        # Log crítico para diagnóstico de SendGrid
        logger.warning(
            "EMAIL SEND ATTEMPT | raw_from=%r | safe_from=%r | recipients=%s | attachment=%s",
            raw_from,
            safe_from,
            destinatarios,
            arquivo_excel,
        )

        # Cria o email
        email = EmailMessage(
            subject=assunto,
            body=corpo,
            from_email=safe_from,
            to=destinatarios,
        )

        # Anexa o arquivo
        email.attach_file(arquivo_excel)

        # Envia
        email.send(fail_silently=False)

        logger.info(
            "EMAIL SENT SUCCESS | from=%s | to=%s | subject=%s",
            safe_from,
            ",".join(destinatarios),
            assunto,
        )

        return True

    except Exception:
        # Loga stack trace completo (sem print)
        logger.exception(
            "EMAIL SEND FAILED | from=%r | recipients=%s | attachment=%s",
            raw_from,
            destinatarios,
            arquivo_excel,
        )
        return False
