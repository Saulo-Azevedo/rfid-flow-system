# API – Integrações (RFID Flow)

## 📋 Visão Geral

O **RFID Flow** disponibiliza uma API HTTP para integração com dispositivos coletores RFID, leitores de código de barras e sistemas externos. A API é responsável por registrar leituras, consultar dados e alimentar dashboards.

Toda a especificação é documentada via **Swagger / OpenAPI**.

---

## 🛰️ Endpoint – Registro de Leitura RFID

Registra uma leitura enviada por um coletor. Se o botijão não existir, ele é criado automaticamente.

* **Método:** `POST`
* **URL:** `/api/registrar-leitura/`

### 🔍 Parâmetros do Body

| Campo | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `tag_rfid` | string | **Sim** | EPC / Tag RFID lida pelo coletor |
| `operador` | string | Não | Identificação do dispositivo ou operador |
| `observacao` | string | Não | Observação livre associada à leitura |

### 📥 Respostas Disponíveis

| Status | Descrição | Exemplo de JSON |
| :--- | :--- | :--- |
| **200** | Sucesso | `{"success": true, "message": "Sucesso", "id_leitura": 123}` |
| **400** | Requisição Inválida | `{"success": false, "error": "Tag RFID faltando"}` |
| **405** | Método Incorreto | `{"success": false, "error": "Use POST"}` |
| **500** | Erro Interno | `{"success": false, "error": "Descrição do erro"}` |

---

## 📊 Endpoints de Dashboard e Relatórios (AJAX)

| Endpoint | Método | Descrição |
| :--- | :--- | :--- |
| `/api/dashboard/` | `GET` | Dados consolidados (total cilindros, leituras 7 dias, etc) |
| `/api/relatorios/` | `GET` | Consulta estruturada para filtros e análises |

---

## 🛠️ Ambientes e Versionamento

**Tabela de Ambientes**

* **Local:** `http://127.0.0.1:8000`
* **Homologação:** `https://<dominio-hml>`
* **Produção:** `https://<dominio-prod>`

> **Nota sobre Versionamento:** Atualmente a API não usa prefixo de versão. Recomenda-se o uso futuro de `/api/v1/` para evitar quebras de compatibilidade.

---
⚠️ *A documentação Swagger reflete automaticamente os endpoints disponíveis e ativos.*