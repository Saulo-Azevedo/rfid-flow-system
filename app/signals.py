import os
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


def env_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


@receiver(post_migrate)
def ensure_superuser(sender, **kwargs):
    """
    Roda automaticamente após migrations.
    Cria/atualiza superusuário usando variáveis de ambiente.
    """
    username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()
    password = (os.getenv("DJANGO_SUPERUSER_PASSWORD") or "").strip()
    reset_password = env_bool("DJANGO_SUPERUSER_RESET_PASSWORD", "0")

    # Sem vars => não faz nada (não quebra deploy)
    if not username or not email or not password:
        print("⚠️ post_migrate: DJANGO_SUPERUSER_* não definidos. Pulando superuser.")
        return

    User = get_user_model()

    # Tenta achar por username; se não der, tenta por email
    user = None
    try:
        user = User.objects.filter(username=username).first()
    except Exception:
        user = None

    if user is None:
        try:
            user = User.objects.filter(email=email).first()
        except Exception:
            user = None

    if user is None:
        # Cria superuser (compatível com modelos diferentes)
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"✅ post_migrate: Superusuário criado: {username}")
        except TypeError:
            User.objects.create_superuser(email=email, password=password)
            print(f"✅ post_migrate: Superusuário criado: {email}")
        return

    # Atualiza permissões e (opcionalmente) reseta senha
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
        print(f"🔑 post_migrate: Senha resetada para: {getattr(user, 'username', email)}")

    if changed:
        user.save()
        print(f"✅ post_migrate: Superusuário atualizado: {getattr(user, 'username', email)}")
    else:
        print(f"ℹ️ post_migrate: Superusuário já OK: {getattr(user, 'username', email)}")
