"""
views.py — App 'core'
Vistas del Portal de Noticias CANACINTRA.
Sistema de navegación por categorías + buscador de noticias.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Publicacion, Categoria, Estatus, Archivo, Comentario
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# ─────────────────────────────────────────────
#  Helper: QuerySet de publicaciones publicadas
# ─────────────────────────────────────────────
def _publicaciones_activas():
    """Retorna publicaciones con estatus 'publicada', ordenadas por fecha."""
    return (
        Publicacion.objects
        .filter(estatus__nombre=Estatus.PUBLICADA)
        .select_related('categoria', 'estatus', 'autor')
        .order_by('-fecha_publicacion', '-fecha_creacion')
    )


# ─────────────────────────────────────────────
#  Vista: Portada / Listado principal
# ─────────────────────────────────────────────
def index(request):
    """
    Página principal: muestra las últimas noticias publicadas con paginación.
    Incluye las 5 noticias más actuales para el carrusel superior.
    """
    qs = _publicaciones_activas()
    recientes = qs[:5]  # Para el carrusel solicitado en hazlo.md
    
    # El listado de abajo puede empezar después de las destacadas o incluir todas
    paginator = Paginator(qs, 9)
    pagina = request.GET.get('pagina', 1)
    noticias_paginadas = paginator.get_page(pagina)

    categorias = Categoria.objects.all().order_by('nombre')

    context = {
        'recientes': recientes,
        'noticias': noticias_paginadas,
        'categorias': categorias,
        'titulo_pagina': 'Noticias CANACINTRA',
    }
    return render(request, 'core/index.html', context)


# ─────────────────────────────────────────────
#  Vista: Detalle de publicación
# ─────────────────────────────────────────────
def publicacion_detalle(request, slug):
    """
    Muestra el contenido completo de una publicación.
    Incrementa el contador de vistas.
    Gestiona el envío de comentarios.
    """
    publicacion = get_object_or_404(
        Publicacion,
        slug=slug,
        estatus__nombre=Estatus.PUBLICADA,
    )

    if request.method == 'POST' and request.user.is_authenticated:
        texto = request.POST.get('texto', '').strip()
        if texto:
            Comentario.objects.create(
                publicacion=publicacion,
                usuario=request.user,
                texto=texto,
                estado=Comentario.ESTADO_PENDIENTE
            )
            messages.success(request, 'Tu comentario aparecerá una vez que sea revisado por un administrador.')
            return redirect('core:publicacion_detalle', slug=slug)

    # Incrementar contador de vistas
    Publicacion.objects.filter(pk=publicacion.pk).update(vistas=publicacion.vistas + 1)
    publicacion.vistas += 1

    archivos = publicacion.archivos.all()
    comentarios = publicacion.comentarios.filter(estado=Comentario.ESTADO_APROBADO).select_related('usuario')

    # Noticias relacionadas de la misma categoría
    relacionadas = (
        _publicaciones_activas()
        .filter(categoria=publicacion.categoria)
        .exclude(pk=publicacion.pk)[:4]
    )

    context = {
        'publicacion': publicacion,
        'archivos': archivos,
        'comentarios': comentarios,
        'relacionadas': relacionadas,
        'categorias': Categoria.objects.all(),
        'titulo_pagina': publicacion.titulo,
    }
    return render(request, 'core/publicacion_detalle.html', context)


# ─────────────────────────────────────────────
#  Vista: Filtrado por categoría
# ─────────────────────────────────────────────
def categoria_detalle(request, slug):
    """
    Muestra todas las publicaciones de una categoría específica.
    Navegación por categorías del portal.
    """
    categoria = get_object_or_404(Categoria, slug=slug)
    qs = _publicaciones_activas().filter(categoria=categoria)

    paginator = Paginator(qs, 9)
    pagina = request.GET.get('pagina', 1)
    noticias = paginator.get_page(pagina)

    categorias = Categoria.objects.all().order_by('nombre')

    context = {
        'categoria': categoria,
        'noticias': noticias,
        'categorias': categorias,
        'titulo_pagina': f'Categoría: {categoria.nombre}',
    }
    return render(request, 'core/categoria.html', context)


# ─────────────────────────────────────────────
#  Vista: Buscador de noticias
# ─────────────────────────────────────────────
@require_GET
def buscar(request):
    """
    Buscador de noticias por título, contenido o resumen.
    Busca en publicaciones con estatus 'publicada'.
    """
    query = request.GET.get('q', '').strip()
    resultados = Publicacion.objects.none()
    categorias = Categoria.objects.all().order_by('nombre')

    if query and len(query) >= 2:
        resultados = (
            _publicaciones_activas()
            .filter(
                Q(titulo__icontains=query) |
                Q(contenido__icontains=query) |
                Q(resumen__icontains=query) |
                Q(categoria__nombre__icontains=query)
            )
            .distinct()
        )

    paginator = Paginator(resultados, 9)
    pagina = request.GET.get('pagina', 1)
    noticias = paginator.get_page(pagina)

    context = {
        'query': query,
        'noticias': noticias,
        'total': resultados.count() if query else 0,
        'categorias': categorias,
        'titulo_pagina': f'Búsqueda: {query}' if query else 'Buscar noticias',
    }
    return render(request, 'core/buscar.html', context)


# ─────────────────────────────────────────────
#  Vista: Buscador AJAX (sugerencias en tiempo real)
# ─────────────────────────────────────────────
@require_GET
def buscar_ajax(request):
    """
    Endpoint AJAX para autocompletado del buscador.
    Devuelve hasta 5 sugerencias en formato JSON.
    """
    query = request.GET.get('q', '').strip()
    datos = []

    if query and len(query) >= 2:
        sugerencias = (
            _publicaciones_activas()
            .filter(
                Q(titulo__icontains=query) | Q(resumen__icontains=query)
            )[:5]
        )
        datos = [
            {
                'titulo': pub.titulo,
                'url': pub.get_absolute_url(),
                'categoria': pub.categoria.nombre,
                'fecha': pub.fecha_publicacion.strftime('%d %b %Y') if pub.fecha_publicacion else '',
            }
            for pub in sugerencias
        ]

    return JsonResponse({'resultados': datos, 'query': query})


# ─────────────────────────────────────────────
#  Vista: Redirección post-login según rol
# ─────────────────────────────────────────────
@login_required
def login_redirect(request):
    """
    Redirige al usuario tras iniciar sesión:
    - Admin/Staff -> Panel de Administración
    - Usuario normal -> Portada del sitio
    """
    if request.user.is_superuser:
        return redirect('/admin/')
    return redirect('core:index')


def registro(request):
    """Vista para el registro de nuevos usuarios."""
    if request.user.is_authenticated:
        return redirect('core:index')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Cuenta creada exitosamente! Ya puedes iniciar sesión.')
            return redirect('core:login')
    else:
        form = UserCreationForm()
    
    return render(request, 'core/registro.html', {'form': form})
