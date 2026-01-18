# API (Integrações)

## Visão geral
A aplicação expõe endpoints para registrar leituras e obter dados do dashboard.

### Registro de leitura RFID
- **Endpoint:** `POST /api/registrar-leitura/`
- **Objetivo:** registrar uma leitura RFID.

> Observação: o payload exato deve refletir o formato enviado pelo coletor. Documente aqui com exemplos reais do cliente.

### Barcode
- **Página de leitura:** `GET /api/barcode/leitura/`
- **Registrar:** `POST /api/barcode/registrar/`
- **Dados para dashboard:** `GET /api/barcode/dashboard/`

## Recomendação (padrão de mercado)
- Adicionar Swagger/OpenAPI para referência automatizada.
- Versionar endpoints (ex: `/api/v1/...`).
