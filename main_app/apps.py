from django.apps import AppConfig


class MainAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_app'
    
class MediaApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'media_api'
