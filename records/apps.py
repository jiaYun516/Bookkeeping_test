from django.apps import AppConfig

class RecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'records'

    def ready(self):
        import records.signals  # 在 App 準備好時載入信號