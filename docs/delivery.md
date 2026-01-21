# Entrega ao Cliente

Esta página descreve o pacote de entrega do **RFID Flow**, incluindo URLs, acessos iniciais, responsabilidades, checklist de aceite e suporte.

> **Nota importante**  
> Este projeto está sendo entregue como uma **Prova de Conceito (POC) / MVP**, com o objetivo de validar fluxos, integrações e viabilidade operacional.  
> Algumas funcionalidades podem evoluir, ser ajustadas ou expandidas conforme o uso real e o feedback do cliente.

---

## URLs

- **Sistema (Produção / Railway):**  
  https://web-production-fd2d9.up.railway.app/login/

- **Documentação (GitHub Pages):**  
  https://saulo-azevedo.github.io/rfid-flow-system/

- **Swagger (API Docs):**  
  https://web-production-fd2d9.up.railway.app/api/docs/

- **OpenAPI Schema:**  
  https://web-production-fd2d9.up.railway.app/api/schema/

---

## Acessos iniciais

> Recomenda-se **trocar a senha no primeiro acesso**.  
> As credenciais iniciais são entregues por **canal seguro**, fora deste documento.

- **Administrador**
  - Usuário: `<Ver documentação auxiliar>`
  - E-mail: `<Ver documentação auxiliar>`
  - Senha: `<Ver documentação auxiliar>`

- **Operador**
  - Usuário: `<Ver documentação auxiliar>`
  - E-mail: `<Ver documentação auxiliar>`
  - Senha: `<Ver documentação auxiliar>`
  - Permissões: acesso operacional (sem funções administrativas)

---

## Backup e histórico de dados

### Definição de responsabilidades

#### Responsabilidade do fornecedor (RFID Flow)

- Disponibilizar os **meios técnicos** para acesso aos dados e geração de relatórios.
- Apoiar o cliente na **orientação inicial** sobre exportação e boas práticas de backup.
- Garantir o funcionamento do sistema conforme o escopo definido para o MVP.

#### Responsabilidade do cliente

Cabe ao cliente:

- Definir e manter sua **política interna de retenção de dados**, de acordo com normas operacionais, fiscais ou regulatórias.
- Garantir a **guarda segura das cópias de relatórios exportados** (ex.: arquivos Excel), incluindo armazenamento local ou em nuvem sob sua gestão.
- Acompanhar e validar a **periodicidade dos backups**, conforme acordado no momento da entrega.
- Solicitar testes de restauração ou suporte adicional sempre que necessário.

---

### Procedimento mínimo recomendado de backup

Para garantir a integridade e a rastreabilidade dos dados, recomenda-se, no mínimo:

1. **Exportação periódica de relatórios (Excel)**  
   - Periodicidade definida em conjunto (ex.: diária, semanal ou mensal).  
   - Armazenamento em local seguro sob responsabilidade do cliente.

2. **Backup do banco de dados (Railway – PostgreSQL)**  
   - Utilização dos mecanismos de backup disponibilizados pela plataforma de hospedagem.  
   - Manutenção conforme a política acordada (frequência e retenção).

3. **Verificação periódica de restauração**  
   - Realização de teste de restauração em intervalos regulares (recomendado: mensal).  
   - Objetivo: garantir que os backups estejam íntegros e utilizáveis em caso de necessidade.

> **Observação:** o RFID Flow não substitui políticas internas de backup e retenção de dados do cliente, atuando como ferramenta de apoio à operação e à geração de informações.

---

## Checklist de validação (Aceite)

Marcar como **OK** quando validado em produção.

### Acesso e navegação
- [ ] Login OK  
- [ ] Logout OK  
- [ ] Reset de senha OK (envio e troca)

### Leitura e operação
- [ ] Leitura RFID (TAG) OK  
- [ ] Leitura Código de Barras OK  
- [ ] Inventário (iniciar/parar e contabilização) OK

### Relatórios e exportações
- [ ] Relatórios (tela) OK  
- [ ] Exportação Excel OK  
- [ ] Envio de relatório por e-mail OK

### API / Integrações
- [ ] Swagger abre (`/api/docs/`) OK  
- [ ] Endpoint RFID – registrar leitura OK  
- [ ] Endpoint Barcode – registrar leitura OK

> O aceite é considerado concluído após a validação positiva dos itens acima.

---

## Suporte

- **Canais de atendimento:**
  - WhatsApp: `<.......>`
  - E-mail: `<........>`

- **Horário de atendimento:**
  - `<ex.: Segunda a Sexta, 08:00–18:00>`

- **Tempo de resposta estimado (SLA):**
  - Incidente crítico: `<ex.: até 2h>`
  - Incidente normal: `<ex.: até 8h>`
  - Dúvidas / melhorias: `<ex.: até 2 dias úteis>`

> **Observação:** por se tratar de um MVP, os tempos de resposta podem variar conforme a complexidade e a prioridade do atendimento.

---

## Observações finais

- **Versão entregue:** V1 – Prova de Conceito (MVP)
- **Data de entrega:** `<DD/MM/AAAA>`
- **Ambiente:** Produção (Railway)

---
Documento referente à versão **v1.0 (MVP)** do RFID Flow.