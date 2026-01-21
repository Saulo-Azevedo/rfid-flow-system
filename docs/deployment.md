# Deploy — Produção (Railway)

Este documento descreve o processo técnico de implantação do RFID Flow.

---

## Variáveis de Ambiente

Obrigatórias:
- SECRET_KEY
- DEBUG=0
- DATABASE_URL
- ALLOWED_HOSTS
- CSRF_TRUSTED_ORIGINS

Opcionais (e-mail):
- EMAIL_BACKEND
- EMAIL_HOST
- EMAIL_PORT
- EMAIL_USE_TLS
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD
- DEFAULT_FROM_EMAIL

---

## Comando de Start

```bash
python manage.py migrate && \
python manage.py collectstatic --noinput && \
gunicorn app.wsgi
```
## Backup (Exemplo)
pg_dump "$DATABASE_URL" > backup_YYYYMMDD.sql


---

## 📄 4️⃣ DELIVERY — JÁ ESTÁ CORRETO
O `delivery.md` que você aprovou **já está perfeito** e alinhado com os outros.

---

## ✅ PRÓXIMOS PASSOS (SEM RISCO)

```bash
git checkout -b docs/final-docs
# substituir os 4 arquivos
mkdocs build -s
git add docs/
git commit -m "docs: finalize operator, admin, deploy and delivery documentation"
git push -u origin docs/final-docs
