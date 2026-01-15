import os
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

print("📌 rfid.signals importado (signals carregados)!")

def env_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")

@receiver(post_migrate)
def ensure_superuser(sender, **kwargs):
    print(f"🧩 post_migrate disparou para: {getattr(sender, 'name', sender)}")

    username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()
    password = (os.getenv("DJANGO_SUPERUSER_PASSWORD") or "").strip()
    reset_password = env_bool("DJANGO_SUPERUSER_RESET_PASSWORD", "0")

    if not username or not email or not password:
        print("⚠️ post_migrate: DJANGO_SUPERUSER_* não definidos. Pulando.")
        return

    User = get_user_model()

    user = User.objects.filter(username=username).first() if hasattr(User, "USERNAME_FIELD") else None
    if user is None and hasattr(User, "email"):
        user = User.objects.filter(email=email).first()

    if user is None:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✅ post_migrate: Superusuário criado: {username}")
        return

    if reset_password:
        user.set_password(password)
        user.save()
        print(f"🔑 post_migrate: senha resetada: {username}")
    else:
        print(f"ℹ️ post_migrate: usuário já existe: {username}")
