# Modelo de Dados

## Entidades principais
- **Botijao** (`rfid.models.Botijao`)
- **LeituraRFID** (`rfid.models.LeituraRFID`)
- **LeituraCodigoBarra** (`rfid.models.LeituraCodigoBarra`)
- **LogAuditoria** (`rfid.models.LogAuditoria`)
- **ImportacaoXLS** (`rfid.models.ImportacaoXLS`)

## Sugestão para vínculo RFID ↔ Barcode
Hoje `Botijao` é identificado por `tag_rfid` (único).
Se o processo do cliente exigir vínculo, as opções comuns são:

1. Adicionar campo `codigo_barra` em `Botijao` (único, opcional)
2. Criar tabela de relação `Identificador` (tipo: RFID/BARCODE, valor, ativo) e vincular ao Botijao

## Diagrama Modelo De Dados :

![Modelo de dados](images/models.png)
