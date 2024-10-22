from django.apps import AppConfig

class Beyondcomv2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BeyondComV2'

    def ready(self):
        import BeyondComV2.signals  # Assurez-vous que le fichier signals.py existe