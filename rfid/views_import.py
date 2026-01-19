# rfid/views_import.py

import pandas as pd
from django.contrib import messages
from django.shortcuts import redirect, render

from .models import Botijao, LeituraRFID


# =============================
# 1) UPLOAD — apenas exibe formulário
# =============================
def upload_xls(request):
    return render(request, "rfid/dj_upload_xls.html")


# =============================
# 2) PREVIEW — Lê XLS e mostra prévia
# =============================
def preview_import(request):
    if request.method != "POST":
        return redirect("upload_xls")

    arquivo = request.FILES.get("arquivo")

    if not arquivo:
        messages.error(request, "Nenhum arquivo enviado.")
        return redirect("upload_xls")

    # Lê arquivo XLS
    try:
        df = pd.read_excel(arquivo)
    except Exception as e:
        messages.error(request, f"Erro ao ler arquivo XLS: {e}")
        return redirect("upload_xls")

    # Converte para lista de dicionários
    dados = df.to_dict(orient="records")

    # Armazena na sessão (para confirmar depois)
    request.session["import_preview"] = dados

    return render(request, "rfid/preview_import.html", {"dados": dados})


# =============================
# 3) CONFIRMAR — Salva no banco
# =============================
def confirmar_import(request):
    dados = request.session.get("import_preview")

    if not dados:
        messages.error(request, "Nenhum dado para importar.")
        return redirect("upload_xls")

    novos = 0
    leituras = 0

    for linha in dados:
        tag = str(linha.get("EPC", "")).strip()

        if not tag:
            continue

        # Busca ou cria botijão
        botijao, criado = Botijao.objects.get_or_create(tag_rfid=tag)

        if criado:
            novos += 1

        # Cria leitura associada
        LeituraRFID.objects.create(botijao=botijao)
        leituras += 1

    # Limpa prévia da sessão
    request.session.pop("import_preview", None)

    return render(
        request,
        "rfid/confirmar_import.html",
        {
            "novos_botijoes": novos,
            "qtd": leituras,
        },
    )
