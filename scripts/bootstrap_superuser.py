import os
import sys


def env_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


def main() -> int:
    # Seu projeto Django (pasta que tem settings.py) é "rfid"
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        os.getenv("DJANGO_SETTINGS_MODULE", "rfid.settings").strip()
    )

    import django
    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()
    password = (os.getenv("DJANGO_SUPERUSER_PASSWORD") or "").strip()

    # Flag para resetar senha quando necessário (use "1" temporariamente)
    reset_password = env_bool("DJANGO_SUPERUSER_RESET_PASSWORD", "0")

    # Se faltarem variáveis, não quebra deploy; só avisa e segue
    if not username or not email or not password:
        print("⚠️ DJANGO_SUPERUSER_* não definidos (USERNAME/EMAIL/PASSWORD). Pulando bootstrap do superusuário.")
        return 0

    # 1) Tenta achar por username
    user = None
    try:
        user = User.objects.filter(username=username).first()
    except Exception:
        # Caso o User model não tenha campo username
        user = None

    # 2) Se não achou por username, tenta por email (se existir)
    if user is None:
        try:
            user = User.objects.filter(email=email).first()
        except Exception:
            user = None

    # Criação
    if user is None:
        try:
            # Modelo padrão do Django (username + email)
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
        except TypeError:
            # Alguns projetos usam email como identificador (sem username)
            # Tentamos criar superuser com email apenas
            user = User.objects.create_superuser(
                email=email,
                password=password
            )

        print(f"✅ Superusuário criado: {getattr(user, 'username', email)}")
        return 0

    # Já existe: garante permissões e dados básicos
    changed = False

    if not getattr(user, "is_staff", False):
        user.is_staff = True
        changed = True

    if not getattr(user, "is_superuser", False):
        user.is_superuser = True
        changed = True

    # Atualiza email se o campo existir e estiver diferente
    if hasattr(user, "email") and email and user.email != email:
        user.email = email
        changed = True

    # Reset de senha controlado por flag
    if reset_password:
        user.set_password(password)
        changed = True
        print(f"🔑 Senha do superusuário resetada: {getattr(user, 'username', email)}")

    if changed:
        user.save()
        print(f"✅ Superusuário atualizado: {getattr(user, 'username', email)}")
    else:
        print(f"ℹ️ Superusuário já existe e está OK: {getattr(user, 'username', email)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
