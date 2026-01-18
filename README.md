# RFID Flow System

Sistema web para controle de botijões/cilindros utilizando **RFID UHF** e **código de barras**.

## Principais funcionalidades
- Registro de leituras RFID e barcode
- Histórico e relatórios
- Importação via planilha (XLS/XLSX)
- Envio de relatório por e-mail (configurável)

## Stack
- Python + Django
- PostgreSQL (produção) / SQLite (desenvolvimento)
- Deploy: Railway (Nixpacks)

## Como rodar localmente
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Variáveis de ambiente
Veja `.env.example`.

## Documentação
Este repositório inclui documentação em MkDocs:
```bash
pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin
mkdocs serve
```

Para gerar HTML:
```bash
mkdocs build
```

## Rotas úteis
- Dashboard: `/`
- Login: `/login/`
- Admin: `/admin/`
- API RFID: `/api/registrar-leitura/`
- API Barcode: `/api/barcode/registrar/`
