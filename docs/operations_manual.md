# Manual do Operador

## Objetivo
Registrar e consultar leituras de botijões via RFID e/ou código de barras.

## Acesso
1. Acesse a URL do sistema
2. Faça login
3. Utilize o dashboard (página inicial)

## Fluxo operacional (leitura)
- **RFID:** quando uma tag é lida, o sistema registra um evento e atualiza o histórico.
- **Barcode:** quando um código é lido, o sistema registra um evento e atualiza o histórico.

### Cenários comuns
- **Botijão sem tag (apenas barcode):** registrar via barcode normalmente.
- **Botijão sem barcode (apenas tag):** registrar via RFID normalmente.

## Relatórios
- Tela de relatórios permite filtros e exportação.
- Exportação para Excel e envio por e-mail dependem das permissões e configuração.

## Boas práticas de operação
- Garantir que o dispositivo esteja com data/hora corretas
- Conferir conectividade (Wi-Fi/4G) quando a integração é online
- Em falha recorrente, reportar com horário aproximado e identificação do dispositivo
