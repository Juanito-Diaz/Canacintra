"""
admin.py — App 'core'
Configuración avanzada del Admin de Django para el portal CANACINTRA.
Incluye: filtros laterales por Estatus/Categoría, búsqueda por título,
acciones masivas y visualización enriquecida.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Publicacion, Categoria, Estatus, Archivo, Perfil


# ─────────────────────────────────────────────
#  Inline: Archivos adjuntos en la publicación
# ─────────────────────────────────────────────
class ArchivoInline(admin.TabularInline):
    model = Archivo
    extra = 1
    fields = ('nombre', 'tipo', 'archivo', 'tamanio_bytes')
    readonly_fields = ('tamanio_bytes',)
    verbose_name = 'Archivo adjunto'
    verbose_name_plural = 'Archivos adjuntos'


# ─────────────────────────────────────────────
#  Admin: Publicación
# ─────────────────────────────────────────────
@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    # Columnas visibles en el listado
    list_display = (
        'titulo_truncado',
        'categoria',
        'estatus_badge',
        'autor',
        'fecha_creacion',
        'fecha_publicacion',
        'vistas',
        'imagen_preview',
    )
    # Filtros laterales
    list_filter = (
        'estatus',
        'categoria',
        'autor',
        ('fecha_publicacion', admin.DateFieldListFilter),
    )
    # Búsqueda por título y contenido
    search_fields = ('titulo', 'contenido', 'resumen')
    # Slugs y fechas auto-completados
    prepopulated_fields = {'slug': ('titulo',)}
    readonly_fields = ('fecha_creacion', 'vistas')
    # Ordenación por defecto
    ordering = ('-fecha_creacion',)
    # Número de elementos por página
    list_per_page = 20
    # Inlines
    inlines = [ArchivoInline]
    # Campos del formulario de edición organizados por secciones
    fieldsets = (
        ('Información Principal', {
            'fields': ('titulo', 'slug', 'resumen', 'contenido'),
        }),
        ('Imagen Destacada', {
            'fields': ('imagen_destacada',),
        }),
        ('Clasificación', {
            'fields': ('categoria', 'estatus', 'autor'),
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_publicacion', 'vistas'),
            'classes': ('collapse',),
        }),
    )
    # Acciones masivas personalizadas
    actions = ['publicar_seleccionadas', 'enviar_a_revision', 'despublicar']

    def titulo_truncado(self, obj):
        return obj.titulo[:60] + '…' if len(obj.titulo) > 60 else obj.titulo
    titulo_truncado.short_description = 'Título'

    def estatus_badge(self, obj):
        """Muestra el estatus con un badge de color."""
        colores = {
            'captura': '#6c757d',
            'revision': '#fd7e14',
            'publicada': '#198754',
        }
        nombre = obj.estatus.nombre if obj.estatus else ''
        color = colores.get(nombre, '#6c757d')
        etiqueta = obj.estatus.get_nombre_display() if obj.estatus else '—'
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;'
            'border-radius:12px;font-size:0.8em;font-weight:600;">{}</span>',
            color, etiqueta
        )
    estatus_badge.short_description = 'Estatus'

    def imagen_preview(self, obj):
        if obj.imagen_destacada:
            return format_html(
                '<img src="{}" style="width:50px;height:35px;object-fit:cover;'
                'border-radius:4px;" />',
                obj.imagen_destacada.url
            )
        return '—'
    imagen_preview.short_description = 'Imagen'

    # ── Acciones masivas ──
    @admin.action(description='✅ Publicar seleccionadas')
    def publicar_seleccionadas(self, request, queryset):
        estatus_pub, _ = Estatus.objects.get_or_create(nombre=Estatus.PUBLICADA)
        count = queryset.update(estatus=estatus_pub, fecha_publicacion=timezone.now())
        self.message_user(request, f'{count} publicación(es) publicadas exitosamente.')

    @admin.action(description='🔍 Enviar a revisión')
    def enviar_a_revision(self, request, queryset):
        estatus_rev, _ = Estatus.objects.get_or_create(nombre=Estatus.REVISION)
        count = queryset.update(estatus=estatus_rev)
        self.message_user(request, f'{count} publicación(es) enviadas a revisión.')

    @admin.action(description='⛔ Despublicar (pasar a Captura)')
    def despublicar(self, request, queryset):
        estatus_cap, _ = Estatus.objects.get_or_create(nombre=Estatus.CAPTURA)
        count = queryset.update(estatus=estatus_cap, fecha_publicacion=None)
        self.message_user(request, f'{count} publicación(es) movidas a Captura.')


# ─────────────────────────────────────────────
#  Admin: Categoría
# ─────────────────────────────────────────────
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'total_publicaciones', 'creada_en')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    ordering = ('nombre',)

    def total_publicaciones(self, obj):
        return obj.publicaciones.count()
    total_publicaciones.short_description = 'Publicaciones'


# ─────────────────────────────────────────────
#  Admin: Estatus
# ─────────────────────────────────────────────
@admin.register(Estatus)
class EstatusAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_nombre_display', 'total_publicaciones')
    ordering = ('nombre',)

    def total_publicaciones(self, obj):
        return obj.publicaciones.count()
    total_publicaciones.short_description = 'Publicaciones'


# ─────────────────────────────────────────────
#  Admin: Archivo
# ─────────────────────────────────────────────
@admin.register(Archivo)
class ArchivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'publicacion', 'subido_por', 'tamanio_legible', 'subido_en')
    list_filter = ('tipo',)
    search_fields = ('nombre', 'publicacion__titulo')
    readonly_fields = ('tamanio_bytes', 'subido_en')

    def tamanio_legible(self, obj):
        return obj.tamanio_legible
    tamanio_legible.short_description = 'Tamaño'


# ─────────────────────────────────────────────
#  Admin: Perfil
# ─────────────────────────────────────────────
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'avatar_preview', 'telefono', 'creado_en')
    list_filter = ('rol',)
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name')

    def avatar_preview(self, obj):
        if obj.foto_perfil:
            return format_html(
                '<img src="{}" style="width:35px;height:35px;object-fit:cover;'
                'border-radius:50%;" />',
                obj.foto_perfil.url
            )
        return '👤'
    avatar_preview.short_description = 'Avatar'


# ─────────────────────────────────────────────
#  Personalización del sitio de administración
# ─────────────────────────────────────────────
admin.site.site_header = 'Portal de Noticias CANACINTRA'
admin.site.site_title = 'CANACINTRA Admin'
admin.site.index_title = 'Panel de Administración'
