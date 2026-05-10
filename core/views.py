"""
views.py — App 'core'
Vistas del Portal de Noticias CANACINTRA.
Sistema de navegación por categorías + buscador de noticias.
"""

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Publicacion, Categoria, Estatus, Archivo


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
    Incluye las 3 noticias más recientes como 'destacadas'.
    """
    qs = _publicaciones_activas()
    destacadas = qs[:3]
    resto = qs[3:]

    paginator = Paginator(resto, 9)
    pagina = request.GET.get('pagina', 1)
    noticias_paginadas = paginator.get_page(pagina)

    categorias = Categoria.objects.all().order_by('nombre')

    context = {
        'destacadas': destacadas,
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
    """
    publicacion = get_object_or_404(
        Publicacion,
        slug=slug,
        estatus__nombre=Estatus.PUBLICADA,
    )

    # Incrementar contador de vistas
    Publicacion.objects.filter(pk=publicacion.pk).update(vistas=publicacion.vistas + 1)
    publicacion.vistas += 1

    archivos = publicacion.archivos.all()

    # Noticias relacionadas de la misma categoría
    relacionadas = (
        _publicaciones_activas()
        .filter(categoria=publicacion.categoria)
        .exclude(pk=publicacion.pk)[:4]
    )

    context = {
        'publicacion': publicacion,
        'archivos': archivos,
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
