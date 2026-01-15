from django.apps import AppConfig

class RfidConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rfid"

    def ready(self):
        print("🚀 rfid.apps.RfidConfig.ready() carregou!")  # TESTE
        import rfid.signals  # noqa
