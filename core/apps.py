"""
apps.py — App 'core'
Configuración de la aplicación y registro de señales.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Portal de Noticias'

    def ready(self):
        import core.signals  # noqa: F401 — registrar señales al iniciar
