# Manual do Administrador

## Usuários
- Criar usuários e definir permissões via `/admin/`
- Recomenda-se manter pelo menos 1 usuário administrador

## Cadastros
- O sistema pode criar registros automaticamente quando uma leitura chega sem cadastro.
- Cadastros e regras específicas podem ser ajustados conforme o processo do cliente.

## Importação por planilha
- A funcionalidade de importação fica em `/upload-xls/`
- O fluxo típico é:
  1. Upload
  2. Pré-visualização
  3. Confirmação

## Auditoria
- Registros de auditoria são mantidos no modelo `LogAuditoria`.
