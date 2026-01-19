import os

import pandas as pd
from django.conf import settings
from django.shortcuts import render


def upload_xls(request):
    mensagem = None

    if request.method == "POST":
        arquivo = request.FILES["arquivo"]
        nome = arquivo.name

        # Criar pasta isolada
        destino = os.path.join(settings.MEDIA_ROOT, "uploads_xls")
        os.makedirs(destino, exist_ok=True)

        caminho_arquivo = os.path.join(destino, nome)

        # Salvar arquivo
        with open(caminho_arquivo, "wb+") as destino_arquivo:
            for chunk in arquivo.chunks():
                destino_arquivo.write(chunk)

        # Teste de leitura XLS
        try:
            df = pd.read_excel(caminho_arquivo)
            linhas = len(df)
            mensagem = f"Arquivo recebido e lido com sucesso: {linhas} linhas."
        except Exception as e:
            mensagem = f"Arquivo salvo, mas erro ao ler: {e}"

    return render(request, "dj_upload_xls.html", {"mensagem": mensagem})
