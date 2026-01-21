# Manual do Administrador — RFID Flow

Este manual descreve as funções administrativas do sistema RFID Flow.

---

## 1. Acesso Administrativo

O acesso administrativo é realizado via painel Django:

/admin/


Somente usuários com permissão de administrador podem acessar.

---

## 2. Gestão de Usuários

- Criar usuários
- Definir permissões
- Recomenda-se manter ao menos **1 administrador ativo**

---

## 3. Cadastros e Regras

- O sistema pode criar ativos automaticamente quando recebe leituras sem cadastro prévio.
- Regras específicas podem ser ajustadas conforme o processo do cliente.

---

## 4. Importação por Planilha

Fluxo:
1. Upload
2. Pré-visualização
3. Confirmação

---

## 5. Auditoria

O sistema mantém registros no modelo **LogAuditoria**, incluindo:
- Data/Hora
- Origem
- Operação executada
- Usuário responsável
