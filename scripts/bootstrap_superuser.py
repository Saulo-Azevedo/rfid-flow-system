import os
import sys

def main():
    # 👇 seu projeto Django se chama "rfid"
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        os.getenv("DJANGO_SETTINGS_MODULE", "rfid.settings")
    )

    import django
    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

    if not username or not email or not password:
        print("⚠️ Variáveis DJANGO_SUPERUSER_* não definidas. Pulando criação.")
        return 0

    user = User.objects.filter(username=username).first()
    if user is None:
        user = User.objects.filter(email=email).first()

    if user is None:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print("✅ Superusuário criado:", username)
        return 0

    # Garante permissões
    changed = False
    if not user.is_staff:
        user.is_staff = True
        changed = True
    if not user.is_superuser:
        user.is_superuser = True
        changed = True

    if changed:
        user.save()
        print("✅ Superusuário atualizado:", user.username)
    else:
        print("ℹ️ Superusuário já existe:", user.username)

    return 0


if __name__ == "__main__":
    sys.exit(main())
