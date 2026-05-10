"""
signals.py — App 'core'
Señales de Django: crea/actualiza el Perfil automáticamente al crear/guardar un User.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Perfil


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea un Perfil cuando se registra un nuevo usuario."""
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Sincroniza el Perfil cada vez que se guarda el usuario."""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
