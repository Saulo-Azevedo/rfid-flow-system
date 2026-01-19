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

'''

## 📋 **MAPA COMPLETO DAS ROTAS**

### **🔐 Autenticação**
```
/login/                           → Login do sistema
/logout/                          → Logout do sistema
```

### **🔑 Recuperação de Senha**
```
/password-reset/                  → Solicitar reset de senha
/password-reset/done/             → Confirmação de email enviado
/password-reset-confirm/<uid>/<token>/ → Definir nova senha
/password-reset-complete/         → Senha alterada com sucesso
```

### **🏠 Páginas Principais**
```
/                                 → Dashboard (home)
/nova-leitura/                   → Formulário nova leitura RFID
/relatorios/                     → Relatórios com filtros
```

### **📊 Histórico**
```
/historico/buscar/               → 🆕 Buscar histórico (PRINCIPAL)
/historico/                      → Alias (compatibilidade)
/botijao/123/historico/          → Histórico completo de um botijão
```

### **📤 Exportar/Enviar**
```
/exportar-excel/                 → Download Excel
/enviar-email/                   → Enviar por e-mail (PRINCIPAL)
/enviar-relatorio/               → Alias (compatibilidade)
```

### **🔌 APIs AJAX**
```
/api/dashboard/                  → Dados para dashboard
/api/relatorios/                 → Dados para relatórios
```

### **📡 API RFID**
```
/api/registrar-leitura/          → Registrar leitura via POST

'''