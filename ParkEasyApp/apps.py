from django.apps import AppConfig


class ParkeasyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ParkEasyApp'

    def ready(self):
        import ParkEasyApp.signals  # Register signals when the app is ready