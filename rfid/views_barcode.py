# rfid/views_barcode.py
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Botijao, LeituraCodigoBarra, LeituraRFID, LogAuditoria


@csrf_exempt
def api_registrar_barcode(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Use POST"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        codigo = data.get("barcode", "").strip()

        if not codigo:
            return JsonResponse(
                {"success": False, "error": "Barcode vazio"}, status=400
            )

        # --------------------------------------------
        # 1) SALVAR leitura de código de barras
        # --------------------------------------------
        leitura = LeituraCodigoBarra.objects.create(
            codigo=codigo,
            origem="PDA",
            operador="Automático",
            observacao="Leitura via API/ABD",
        )

        # --------------------------------------------
        # 2) Criar/obter Botijao sincronizado com RFID
        # --------------------------------------------
        botijao, criado = Botijao.objects.get_or_create(tag_rfid=codigo)

        # contador
        botijao.total_leituras += 1
        botijao.save(update_fields=["total_leituras"])

        # --------------------------------------------
        # 3) Registrar log
        # --------------------------------------------
        try:
            LogAuditoria.criar_log(
                botijao=botijao,
                acao="leitura",
                usuario=None,
                descricao="Leitura automática via Barcode",
                dados_novos={"codigo": codigo},
            )
        except:
            pass

        return JsonResponse(
            {
                "success": True,
                "codigo": codigo,
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
