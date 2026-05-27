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
from django.contrib.auth import update_session_auth_hash

from .models import Publicacion, Categoria, Estatus, Archivo, Comentario, Perfil, GaleriaImagen
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm


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
    Página principal: muestra las noticias agrupadas por categorías,
    e incluye las 5 noticias más recientes en la sección de 'Noticias Recientes'.
    """
    qs = _publicaciones_activas()
    recientes = qs[:5]  # Para el carrusel de noticias recientes
    
    categorias = Categoria.objects.all().order_by('nombre')
    # Pre-cargar las 3 últimas publicaciones publicadas de cada categoría
    for cat in categorias:
        cat.ultimas_publicaciones = (
            cat.publicaciones.filter(estatus__nombre=Estatus.PUBLICADA)
            .select_related('autor')
            .order_by('-fecha_publicacion', '-fecha_creacion')[:3]
        )

    context = {
        'recientes': recientes,
        'categorias': categorias,
        'titulo_pagina': 'Blogy | Tu Portal de Noticias',
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

    # Incrementar contador de vistas solo si no es administrador (staff)
    if not (request.user.is_authenticated and request.user.is_staff):
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
    Redirige al usuario tras iniciar sesión a su perfil de administración.
    """
    return redirect('core:admin_perfil')


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


# ─────────────────────────────────────────────
#  ADMIN FRONT-END PANEL VIEWS (AJAX/SPA Layout)
# ─────────────────────────────────────────────

def _get_dashboard_context(request, active_tab):
    """Helper to determine base template and active tab for dashboard views."""
    if request.user.is_authenticated:
        from .models import Perfil
        Perfil.objects.get_or_create(usuario=request.user)
        
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    base_template = 'core/partials/ajax_base.html' if is_ajax else 'core/dashboard_base.html'
    return {
        'base_template': base_template,
        'active_tab': active_tab,
        'is_ajax': is_ajax,
    }

def _get_user_rol(user):
    try:
        return user.perfil.rol
    except Exception:
        return 'lector'


@login_required
def admin_perfil(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    context = _get_dashboard_context(request, 'perfil')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        
        perfil.telefono = request.POST.get('telefono', '').strip()
        perfil.bio = request.POST.get('bio', '').strip()
        
        if 'foto_perfil' in request.FILES:
            perfil.foto_perfil = request.FILES['foto_perfil']
            
        perfil.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        if not context['is_ajax']:
            return redirect('core:admin_perfil')
            
    context['perfil'] = perfil
    return render(request, 'core/admin_perfil.html', context)


@login_required
def admin_noticias(request):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol not in ['admin', 'editor', 'redactor']:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'noticias'))
        
    if not request.user.is_superuser and rol == 'redactor':
        publicaciones = Publicacion.objects.select_related('autor', 'categoria', 'estatus').filter(autor=request.user).order_by('-fecha_creacion')
    else:
        publicaciones = Publicacion.objects.select_related('autor', 'categoria', 'estatus').all().order_by('-fecha_creacion')
        
    context = _get_dashboard_context(request, 'noticias')
    context['publicaciones'] = publicaciones
    return render(request, 'core/admin_noticias.html', context)


@login_required
def admin_noticia_crear(request):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol not in ['admin', 'editor', 'redactor']:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'noticias'))
        
    context = _get_dashboard_context(request, 'noticias')
    context['user_rol'] = rol
    categorias = Categoria.objects.all()
    estatuses = Estatus.objects.all()
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        contenido = request.POST.get('contenido', '').strip()
        resumen = request.POST.get('resumen', '').strip()
        categoria_id = request.POST.get('categoria', '')
        estatus_id = request.POST.get('estatus', '')
        
        if rol == 'redactor':
            estatus_obj = Estatus.objects.filter(nombre=Estatus.REVISION).first()
            if estatus_obj:
                estatus_id = str(estatus_obj.pk)
        imagen_modo = request.POST.get('imagen_modo', 'archivo')  # 'archivo' o 'url'
        imagen_url_valor = request.POST.get('imagen_url', '').strip()
        
        if not titulo or not contenido or not categoria_id or not estatus_id:
            messages.error(request, 'Por favor completa todos los campos requeridos.')
        else:
            categoria = get_object_or_404(Categoria, pk=categoria_id)
            estatus = get_object_or_404(Estatus, pk=estatus_id)
            
            noticia = Publicacion(
                titulo=titulo,
                contenido=contenido,
                resumen=resumen,
                categoria=categoria,
                estatus=estatus,
                autor=request.user
            )
            
            if imagen_modo == 'archivo':
                if 'imagen_destacada' in request.FILES:
                    noticia.imagen_destacada = request.FILES['imagen_destacada']
                noticia.imagen_url = None
            elif imagen_modo == 'url':
                noticia.imagen_url = imagen_url_valor
                if noticia.imagen_destacada:
                    noticia.imagen_destacada.delete(save=False)
                noticia.imagen_destacada = ''
                
            noticia.save()
            
            # Guardar galería de imágenes (Archivos)
            galeria_archivos = request.FILES.getlist('galeria')
            for f in galeria_archivos:
                GaleriaImagen.objects.create(publicacion=noticia, imagen=f)

            # Guardar galería de imágenes (URLs)
            galeria_urls_texto = request.POST.get('galeria_urls', '')
            if galeria_urls_texto:
                lineas = galeria_urls_texto.splitlines()
                for linea in lineas:
                    url = linea.strip()
                    if url:
                        GaleriaImagen.objects.create(publicacion=noticia, imagen_url=url)

            messages.success(request, 'Publicación creada con éxito.')
            return redirect('core:admin_noticias')
            
    context['categorias'] = categorias
    context['estatuses'] = estatuses
    context['modo'] = 'crear'
    return render(request, 'core/admin_noticias_form.html', context)


@login_required
def admin_noticia_editar(request, pk):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol not in ['admin', 'editor', 'redactor']:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'noticias'))
        
    noticia = get_object_or_404(Publicacion, pk=pk)
    
    if not request.user.is_superuser and rol == 'redactor' and noticia.autor != request.user:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'noticias'))
    context = _get_dashboard_context(request, 'noticias')
    context['user_rol'] = rol
    categorias = Categoria.objects.all()
    estatuses = Estatus.objects.all()
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        contenido = request.POST.get('contenido', '').strip()
        resumen = request.POST.get('resumen', '').strip()
        categoria_id = request.POST.get('categoria', '')
        estatus_id = request.POST.get('estatus', '')
        
        if rol == 'redactor':
            estatus_obj = Estatus.objects.filter(nombre=Estatus.REVISION).first()
            if estatus_obj:
                estatus_id = str(estatus_obj.pk)
        imagen_modo = request.POST.get('imagen_modo', 'archivo')  # 'archivo' o 'url'
        imagen_url_valor = request.POST.get('imagen_url', '').strip()
        
        if not titulo or not contenido or not categoria_id or not estatus_id:
            messages.error(request, 'Por favor completa todos los campos requeridos.')
        else:
            categoria = get_object_or_404(Categoria, pk=categoria_id)
            estatus = get_object_or_404(Estatus, pk=estatus_id)
            
            noticia.titulo = titulo
            noticia.contenido = contenido
            noticia.resumen = resumen
            noticia.categoria = categoria
            noticia.estatus = estatus
            
            if imagen_modo == 'archivo':
                if 'imagen_destacada' in request.FILES:
                    noticia.imagen_destacada = request.FILES['imagen_destacada']
                noticia.imagen_url = None
            elif imagen_modo == 'url':
                noticia.imagen_url = imagen_url_valor
                if noticia.imagen_destacada:
                    noticia.imagen_destacada.delete(save=False)
                noticia.imagen_destacada = ''
                
            noticia.save()
            
            # Eliminar imágenes de galería seleccionadas
            imagenes_a_eliminar = request.POST.getlist('eliminar_galeria')
            if imagenes_a_eliminar:
                GaleriaImagen.objects.filter(pk__in=imagenes_a_eliminar).delete()
            
            # Guardar nuevas imágenes en la galería (Archivos)
            galeria_archivos = request.FILES.getlist('galeria')
            for f in galeria_archivos:
                GaleriaImagen.objects.create(publicacion=noticia, imagen=f)
                
            # Guardar nuevas imágenes en la galería (URLs)
            galeria_urls_texto = request.POST.get('galeria_urls', '')
            if galeria_urls_texto:
                lineas = galeria_urls_texto.splitlines()
                for linea in lineas:
                    url = linea.strip()
                    if url:
                        GaleriaImagen.objects.create(publicacion=noticia, imagen_url=url)

            messages.success(request, 'Publicación actualizada con éxito.')
            return redirect('core:admin_noticia_editar', pk=noticia.pk)
            
    context['noticia'] = noticia
    context['categorias'] = categorias
    context['estatuses'] = estatuses
    context['modo'] = 'editar'
    return render(request, 'core/admin_noticias_form.html', context)


@login_required
def admin_noticia_eliminar(request, pk):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol not in ['admin', 'editor', 'redactor']:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'noticias'))
        
    noticia = get_object_or_404(Publicacion, pk=pk)
    if not request.user.is_superuser and rol == 'redactor' and noticia.autor != request.user:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'noticias'))
        
    noticia = get_object_or_404(Publicacion, pk=pk)
    noticia.delete()
    messages.success(request, 'Publicación eliminada correctamente.')
    return redirect('core:admin_noticias')


@login_required
def admin_comentarios(request):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol not in ['admin', 'editor']:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'comentarios'))
        
    comentarios = Comentario.objects.select_related('usuario', 'publicacion').all().order_by('-fecha_creacion')
    context = _get_dashboard_context(request, 'comentarios')
    context['comentarios'] = comentarios
    return render(request, 'core/admin_comentarios.html', context)


@login_required
def admin_comentario_eliminar(request, pk):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol not in ['admin', 'editor']:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'comentarios'))
        
    comentario = get_object_or_404(Comentario, pk=pk)
    comentario.delete()
    messages.success(request, 'Comentario eliminado correctamente.')
    return redirect('core:admin_comentarios')


@login_required
def admin_comentario_aprobar(request, pk):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol not in ['admin', 'editor']:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'comentarios'))
        
    comentario = get_object_or_404(Comentario, pk=pk)
    comentario.estado = Comentario.ESTADO_APROBADO
    comentario.save()
    messages.success(request, 'Comentario aprobado correctamente.')
    return redirect('core:admin_comentarios')


@login_required
def admin_categorias(request):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol not in ['admin', 'editor']:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'categorias'))
        
    categorias = Categoria.objects.all().order_by('nombre')
    context = _get_dashboard_context(request, 'categorias')
    context['categorias_list'] = categorias
    return render(request, 'core/admin_categorias.html', context)


@login_required
def admin_categoria_crear(request):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol not in ['admin', 'editor']:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'categorias'))
        
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        icono_css = request.POST.get('icono_css', '').strip() or 'bi-tag'
        
        if nombre:
            if Categoria.objects.filter(nombre=nombre).exists():
                messages.error(request, 'Ya existe una categoría con ese nombre.')
            else:
                Categoria.objects.create(nombre=nombre, descripcion=descripcion, icono_css=icono_css)
                messages.success(request, 'Categoría creada con éxito.')
        else:
            messages.error(request, 'El nombre es obligatorio.')
            
    return redirect('core:admin_categorias')


@login_required
def admin_categoria_eliminar(request, pk):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol not in ['admin', 'editor']:
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'categorias'))
        
    categoria = get_object_or_404(Categoria, pk=pk)
    try:
        categoria.delete()
        messages.success(request, 'Categoría eliminada correctamente.')
    except Exception:
        messages.error(request, 'No se puede eliminar la categoría porque tiene publicaciones asociadas.')
        
    return redirect('core:admin_categorias')


@login_required
def admin_usuarios(request):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol != 'admin':
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'usuarios'))
        
    usuarios = User.objects.all().order_by('username')
    context = _get_dashboard_context(request, 'usuarios')
    context['usuarios_list'] = usuarios
    return render(request, 'core/admin_usuarios.html', context)


@login_required
def admin_usuario_crear(request):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol != 'admin':
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'usuarios'))
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        rol = request.POST.get('rol', 'lector')
        
        if username and password and email:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe.')
            else:
                user = User.objects.create_user(
                    username=username, 
                    email=email, 
                    password=password, 
                    first_name=first_name, 
                    last_name=last_name
                )
                if rol in ['admin', 'editor', 'redactor']:
                    user.is_staff = True
                    user.save()
                
                perfil, _ = Perfil.objects.get_or_create(usuario=user)
                perfil.rol = rol
                perfil.save()
                messages.success(request, f'Usuario {username} creado con éxito.')
        else:
            messages.error(request, 'Nombre de usuario, email y contraseña son obligatorios.')
            
    return redirect('core:admin_usuarios')


@login_required
def admin_usuario_eliminar(request, pk):
    rol = _get_user_rol(request.user)
    if not request.user.is_superuser and rol != 'admin':
        return render(request, 'core/partials/access_denied.html', _get_dashboard_context(request, 'usuarios'))
        
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes eliminarte a ti mismo.')
    else:
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        
    return redirect('core:admin_usuarios')


@login_required
def admin_cambiar_contrasena(request):
    context = _get_dashboard_context(request, 'cambiar_contrasena')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada con éxito.')
            if context['is_ajax']:
                form = PasswordChangeForm(request.user)
            else:
                return redirect('core:admin_perfil')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = PasswordChangeForm(request.user)
        
    context['form'] = form
    return render(request, 'core/admin_cambiar_contrasena.html', context)

