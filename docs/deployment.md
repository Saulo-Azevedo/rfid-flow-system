# Deploy (Produção)

Este projeto está preparado para deploy em **Railway** (ver `railway.json`).

## Variáveis de ambiente
Recomendado configurar no provedor (Railway):
- `SECRET_KEY` (obrigatório)
- `DEBUG=0` (obrigatório)
- `DATABASE_URL` (PostgreSQL)
- `ALLOWED_HOSTS` (lista separada por vírgula)
- `CSRF_TRUSTED_ORIGINS` (lista separada por vírgula)

Opcional (e-mail):
- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

## Comando de start (Railway)
Atualmente em `railway.json`:
```bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn app.wsgi
```

## Checklist de produção
- `DEBUG=0`
- `SECRET_KEY` via env
- `ALLOWED_HOSTS` restrito (evitar `*`)
- `CSRF_TRUSTED_ORIGINS` alinhado ao domínio real
- Backup do banco definido (frequência e retenção)

## Backup do banco (exemplo)
Em PostgreSQL:
```bash
pg_dump "$DATABASE_URL" > backup_YYYYMMDD.sql
```
