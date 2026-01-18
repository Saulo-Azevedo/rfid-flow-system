# RFID Flow — Documentação

Este repositório contém o sistema **RFID Flow**, uma aplicação web para controle e rastreabilidade de botijões/cilindros utilizando **RFID UHF** e **código de barras**.

## O que este sistema faz
- Recebe leituras de **RFID** e/ou **barcode** (em fluxos separados)
- Registra histórico de leituras
- Exibe dashboard operacional e relatórios
- Permite importação via planilha (XLS/XLSX)
- Envia relatórios por e-mail (quando configurado)

## Links úteis (rotas)
- Dashboard: `/`
- Login: `/login/`
- Admin: `/admin/`
- Recuperação de senha: `/password-reset/`
- API RFID (registro): `/api/registrar-leitura/`
- API Barcode:
  - Página: `/api/barcode/leitura/`
  - Registrar: `/api/barcode/registrar/`
  - Dashboard: `/api/barcode/dashboard/`

> **Nota de produto:** RFID e barcode podem existir de forma independente (tag perdida, etiqueta danificada, etc.). O vínculo entre eles pode ser implementado conforme o processo do cliente.
