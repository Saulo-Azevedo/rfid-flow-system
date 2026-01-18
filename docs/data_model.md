# Modelo de Dados

## Entidades principais
- **Botijao** (`rfid.models.Botijao`)
- **LeituraRFID** (`rfid.models.LeituraRFID`)
- **LeituraCodigoBarra** (`rfid.models.LeituraCodigoBarra`)
- **LogAuditoria** (`rfid.models.LogAuditoria`)
- **ImportacaoXLS** (`rfid.models.ImportacaoXLS`)

## Sugestão para vínculo RFID ↔ Barcode
Hoje `Botijao` é identificado por `tag_rfid` (único). Se o processo do cliente exigir vínculo, as opções comuns são:
1. Adicionar campo `codigo_barra` em `Botijao` (único, opcional)
2. Criar tabela de relação `Identificador` (tipo: RFID/BARCODE, valor, ativo) e vincular ao Botijao

## Gerando diagrama (opcional)
Se você instalar `django-extensions` + Graphviz:
```bash
python manage.py graph_models -a -g -o docs/images/models.png
```
E então inclua no final:

![Modelo de dados](images/models.png)
