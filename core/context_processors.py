from .models import Comentario, Categoria, Publicacion, Estatus

def core_context(request):
    """
    Context processor para proveer datos globales a todos los templates.
    - conteo_pendientes: Número de comentarios esperando aprobación.
    - categorias: Listado de todas las categorías.
    - recent_publications: Las 3 publicaciones más recientes para el footer.
    """
    context = {
        'categorias': Categoria.objects.all().order_by('nombre'),
        'recent_publications': Publicacion.objects.filter(estatus__nombre=Estatus.PUBLICADA).select_related('categoria', 'autor').order_by('-fecha_publicacion', '-fecha_creacion')[:3]
    }
    if request.user.is_authenticated and request.user.is_staff:
        context['conteo_pendientes'] = Comentario.objects.filter(estado=Comentario.ESTADO_PENDIENTE).count()
    return context
