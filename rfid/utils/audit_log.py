from rfid.models import LogAuditoria

def registrar_log(usuario, acao, objeto, detalhes='', request=None):
    """
    Registra uma ação de auditoria
    
    Args:
        usuario: User que executou a ação (pode ser None para ações do sistema)
        acao: 'criar', 'editar', 'deletar', 'restaurar', 'leitura'
        objeto: Objeto que foi modificado
        detalhes: Informações adicionais sobre a ação
        request: Request HTTP (opcional, para capturar IP)
    
    Returns:
        LogAuditoria: O log criado
    """
    ip = None
    if request:
        # Tenta pegar o IP real (considerando proxies)
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
    
    log = LogAuditoria.objects.create(
        usuario=usuario,
        acao=acao,
        modelo=objeto.__class__.__name__,
        objeto_id=objeto.pk,
        objeto_repr=str(objeto)[:200],  # Limita a 200 caracteres
        detalhes=detalhes,
        ip_address=ip
    )
    
    return log


def registrar_criacao(usuario, objeto, detalhes='', request=None):
    """Atalho para registrar criação"""
    return registrar_log(usuario, 'criar', objeto, detalhes, request)


def registrar_edicao(usuario, objeto, detalhes='', request=None):
    """Atalho para registrar edição"""
    return registrar_log(usuario, 'editar', objeto, detalhes, request)


def registrar_delecao(usuario, objeto, detalhes='', request=None):
    """Atalho para registrar deleção"""
    return registrar_log(usuario, 'deletar', objeto, detalhes, request)


def registrar_restauracao(usuario, objeto, detalhes='', request=None):
    """Atalho para registrar restauração"""
    return registrar_log(usuario, 'restaurar', objeto, detalhes, request)


def registrar_leitura_rfid(usuario, objeto, detalhes='', request=None):
    """Atalho para registrar leitura RFID"""
    return registrar_log(usuario, 'leitura', objeto, detalhes, request)