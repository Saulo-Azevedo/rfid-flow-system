# rfid/views_barcode.py
import json
import base64
import binascii

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Botijao, LeituraCodigoBarra, LogAuditoria


def _normalizar_codigo_lido(valor: str) -> str:
    """
    Recebe:
      - barcode puro: "210203846-742"
      - URL do QR: "https://minhabotija.fogas.com.br/MjEwMjAzODQ2LTc0Mg=="
    Retorna:
      - valor "canônico" para salvar e usar no sistema.
    """
    if not valor:
        return ""

    v = valor.strip()

    # Se vier URL, tenta extrair o último segmento
    if v.lower().startswith(("http://", "https://")):
        token = v.rstrip("/").split("/")[-1].strip()

        # tenta decodificar Base64 (normal e urlsafe)
        try:
            # garante padding correto (base64 precisa de múltiplo de 4)
            pad = "=" * (-len(token) % 4)
            token_padded = token + pad

            # urlsafe lida com '-' e '_' caso apareçam
            decoded = base64.urlsafe_b64decode(token_padded.encode("utf-8"))
            texto = decoded.decode("utf-8").strip()

            # se decodificou e virou texto legível, usa ele
            if texto:
                return texto

        except (binascii.Error, UnicodeDecodeError):
            # se não der pra decodificar, volta pro token "cru"
            return token

        except Exception:
            # não quebra a API por causa de decode
            return token

    # Caso não seja URL, é barcode normal
    return v


@csrf_exempt
def api_registrar_barcode(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Use POST"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        bruto = (data.get("barcode") or "").strip()
        if not bruto:
            return JsonResponse({"success": False, "error": "Barcode vazio"}, status=400)

        codigo = _normalizar_codigo_lido(bruto)

        # 1) Salvar leitura
        leitura = LeituraCodigoBarra.objects.create(
            codigo=codigo,
            origem="PDA",
            operador="Automático",
            observacao="Leitura via API/ABD",
        )

        # 2) Criar/obter Botijao
        # ⚠️ Recomendo depois trocar para um campo apropriado (ex: codigo_barra)
        botijao, criado = Botijao.objects.get_or_create(tag_rfid=codigo)

        botijao.total_leituras += 1
        botijao.save(update_fields=["total_leituras"])

        # 3) Log
        try:
            LogAuditoria.criar_log(
                botijao=botijao,
                acao="leitura",
                usuario=None,
                descricao="Leitura automática via Barcode/QR",
                dados_novos={"codigo_bruto": bruto, "codigo_normalizado": codigo},
            )
        except Exception:
            pass

        return JsonResponse(
            {
                "success": True,
                "codigo": codigo,
                "codigo_bruto": bruto,
                "criado_novo": criado,
                "id_leitura": leitura.id,
                "data_hora": leitura.data_hora.strftime("%d/%m/%Y %H:%M:%S"),
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def pagina_leitura_barcode(request):
    return render(request, "rfid/barcode_leitura.html")


def api_barcode_dashboard(request):
    hoje = timezone.now().date()
    leituras_hoje = LeituraCodigoBarra.objects.filter(data_hora__date=hoje).count()
    ultimas = list(LeituraCodigoBarra.objects.all().order_by("-data_hora")[:20])

    dados = []
    for l in ultimas:
        dados.append(
            {
                "codigo": l.codigo,
                "origem": l.origem,
                "operador": l.operador or "-",
                "observacao": l.observacao or "-",
                "data_hora": l.data_hora.strftime("%d/%m/%Y %H:%M:%S"),
            }
        )

    ultimo = dados[0]["codigo"] if dados else None

    return JsonResponse(
        {
            "success": True,
            "total_hoje": leituras_hoje,
            "ultimo_codigo": ultimo,
            "leituras": dados,
        }
    )
