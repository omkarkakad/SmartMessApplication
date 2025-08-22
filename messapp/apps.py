from django.apps import AppConfig

class MessappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messapp'

    def ready(self):
        import messapp.signals  # Make sure 'messapp' is your actual app name
