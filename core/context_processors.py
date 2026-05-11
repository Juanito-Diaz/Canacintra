from .models import Comentario

def core_context(request):
    """
    Context processor para proveer datos globales a todos los templates.
    - conteo_pendientes: Número de comentarios esperando aprobación.
    """
    context = {}
    if request.user.is_staff:
        context['conteo_pendientes'] = Comentario.objects.filter(estado=Comentario.ESTADO_PENDIENTE).count()
    return context
