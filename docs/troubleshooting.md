# Troubleshooting

## 1) Não consigo acessar (erro 500)
- Verifique se `DATABASE_URL` está correto
- Rode migrações: `python manage.py migrate`
- Verifique logs do servidor (Railway logs)

## 2) Erro 403 (CSRF)
- Ajuste `CSRF_TRUSTED_ORIGINS` para incluir seu domínio de produção

## 3) Leituras não aparecem
- Confirmar se o dispositivo está enviando para o endpoint correto
- Conferir payload e status HTTP
- Conferir conexão com banco

## 4) Arquivos estáticos sem CSS (produção)
- Rodar `python manage.py collectstatic --noinput`
- Confirmar WhiteNoise no `MIDDLEWARE`
