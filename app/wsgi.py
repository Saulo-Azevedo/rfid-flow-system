"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import errno
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")


def _env_bool(name: str, default: str = "0") -> bool:
    return (os.getenv(name, default) or "").strip().lower() in ("1", "true", "yes", "y", "on")


def _acquire_lock(lock_path: str) -> bool:
    """
    Cria um lockfile de forma atômica.
    Em gunicorn com múltiplos workers, evita executar bootstrap várias vezes.
    """
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, b"locked")
        os.close(fd)
        return True
    except OSError as e:
        if e.errno == errno.EEXIST:
            return False
        raise


def _safe_info(key: str) -> dict:
    """
    Não vaza valores: só informa se existe e o tamanho.
    """
    v = os.getenv(key)
    return {"present": v is not None, "len": (len(v) if v else 0)}


def _bootstrap_superuser_once():
    """
    Cria/atualiza superusuário usando variáveis de ambiente.
    Executa uma única vez por container (lock em /tmp).
    """
    lock_path = "/tmp/bootstrap_superuser.lock"
    if not _acquire_lock(lock_path):
        # Já rodou neste container
        return

    # 🔎 DEBUG seguro: prova se as env vars chegam no runtime
    keys = sorted([
        k for k in os.environ.keys()
        if k.startswith("DJANGO_SUPERUSER") or k == "BOOTSTRAP_SUPERUSER"
    ])
    print("🧪 ENV KEYS (safe):", keys)
    print("🧪 ENV CHECK (safe):", {
        "BOOTSTRAP_SUPERUSER": _safe_info("BOOTSTRAP_SUPERUSER"),
        "DJANGO_SUPERUSER_USERNAME": _safe_info("DJANGO_SUPERUSER_USERNAME"),
        "DJANGO_SUPERUSER_EMAIL": _safe_info("DJANGO_SUPERUSER_EMAIL"),
        "DJANGO_SUPERUSER_PASSWORD": _safe_info("DJANGO_SUPERUSER_PASSWORD"),
        "DJANGO_SUPERUSER_RESET_PASSWORD": _safe_info("DJANGO_SUPERUSER_RESET_PASSWORD"),
    })

    # Se você QUISER desativar o bootstrap, setar BOOTSTRAP_SUPERUSER=0
    if not _env_bool("BOOTSTRAP_SUPERUSER", "1"):
        print("ℹ️ BOOTSTRAP: desativado via BOOTSTRAP_SUPERUSER=0")
        return

    from django.contrib.auth import get_user_model

    username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()
    password = (os.getenv("DJANGO_SUPERUSER_PASSWORD") or "").strip()
    reset_password = _env_bool("DJANGO_SUPERUSER_RESET_PASSWORD", "0")

    if not username or not email or not password:
        print("⚠️ BOOTSTRAP: DJANGO_SUPERUSER_* não definidos/chegaram vazios. Não criei superusuário.")
        return

    User = get_user_model()

    # tenta achar por username (padrão)
    user = None
    try:
        user = User.objects.filter(username=username).first()
    except Exception:
        user = None

    # fallback por email
    if user is None and hasattr(User, "email"):
        user = User.objects.filter(email=email).first()

    if user is None:
        # cria superuser (compatível com modelos diferentes)
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"✅ BOOTSTRAP: Superusuário criado: {username}")
        except TypeError:
            User.objects.create_superuser(email=email, password=password)
            print(f"✅ BOOTSTRAP: Superusuário criado: {email}")
        return

    changed = False
    if not getattr(user, "is_staff", False):
        user.is_staff = True
        changed = True
    if not getattr(user, "is_superuser", False):
        user.is_superuser = True
        changed = True
    if hasattr(user, "email") and email and user.email != email:
        user.email = email
        changed = True

    if reset_password:
        user.set_password(password)
        changed = True
        print(f"🔑 BOOTSTRAP: senha resetada para: {getattr(user, 'username', email)}")

    if changed:
        user.save()
        print(f"✅ BOOTSTRAP: Superusuário atualizado: {getattr(user, 'username', email)}")
    else:
        print(f"ℹ️ BOOTSTRAP: Superusuário já OK: {getattr(user, 'username', email)}")


# Primeiro sobe o Django (isso faz django.setup internamente)
application = get_wsgi_application()

# Depois executa o bootstrap (já com Django pronto)
_bootstrap_superuser_once()
