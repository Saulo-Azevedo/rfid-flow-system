from django.apps import AppConfig

class AppConfigRFID(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        # Importa signals para registrar o post_migrate
        import app.signals  # noqa
