import os
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


def env_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


@receiver(post_migrate)
def ensure_superuser(sender, **kwargs):
    # Evita rodar para apps “aleatórios” (opcional, mas bom)
    # Se quiser mais estrito, descomente e ajuste:
    # if sender.name != "rfid":
    #     return

    username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()
    password = (os.getenv("DJANGO_SUPERUSER_PASSWORD") or "").strip()
    reset_password = env_bool("DJANGO_SUPERUSER_RESET_PASSWORD", "0")

    if not username or not email or not password:
        print("⚠️ post_migrate: DJANGO_SUPERUSER_* não definidos. Pulando.")
        return

    User = get_user_model()

    user = None
    # tenta por username (padrão Django)
    if hasattr(User, "USERNAME_FIELD") and User.USERNAME_FIELD == "username":
        user = User.objects.filter(username=username).first()

    # fallback por email
    if user is None and hasattr(User, "email"):
        user = User.objects.filter(email=email).first()

    if user is None:
        # cria
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"✅ post_migrate: Superusuário criado: {username}")
        except TypeError:
            User.objects.create_superuser(email=email, password=password)
            print(f"✅ post_migrate: Superusuário criado: {email}")
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
        print(f"🔑 post_migrate: Senha resetada: {getattr(user, 'username', email)}")

    if changed:
        user.save()
        print(f"✅ post_migrate: Superusuário atualizado: {getattr(user, 'username', email)}")
    else:
        print(f"ℹ️ post_migrate: Superusuário já OK: {getattr(user, 'username', email)}")
