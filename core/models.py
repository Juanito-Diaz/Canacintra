"""
models.py — App 'core'
Modelos de datos del Portal de Noticias CANACINTRA.
Patrón MVT (Model-View-Template) de Django 5.x.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


# ─────────────────────────────────────────────
#  Categoría
# ─────────────────────────────────────────────
class Categoria(models.Model):
    """Categorías para clasificar publicaciones (ej. Economía, Industria, etc.)."""
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre',
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text='Se genera automáticamente a partir del nombre.',
    )
    icono_css = models.CharField(
        max_length=50,
        blank=True,
        default='bi-tag',
        verbose_name='Icono (Bootstrap Icons)',
        help_text='Ejemplo: bi-graph-up-arrow, bi-buildings, etc.',
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:categoria_detalle', kwargs={'slug': self.slug})


# ─────────────────────────────────────────────
#  Estatus
# ─────────────────────────────────────────────
class Estatus(models.Model):
    """Estados del flujo editorial de una publicación."""
    CAPTURA = 'captura'
    REVISION = 'revision'
    PUBLICADA = 'publicada'

    OPCIONES = [
        (CAPTURA, 'Captura'),
        (REVISION, 'Revisión'),
        (PUBLICADA, 'Publicada'),
    ]

    nombre = models.CharField(
        max_length=20,
        choices=OPCIONES,
        unique=True,
        verbose_name='Nombre del estatus',
    )

    class Meta:
        verbose_name = 'Estatus'
        verbose_name_plural = 'Estatus'
        ordering = ['nombre']

    def __str__(self):
        return self.get_nombre_display()


# ─────────────────────────────────────────────
#  Publicación (Noticia)
# ─────────────────────────────────────────────
class Publicacion(models.Model):
    """Modelo principal de noticias/publicaciones del portal."""
    titulo = models.CharField(
        max_length=255,
        verbose_name='Título',
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
    )
    contenido = models.TextField(
        verbose_name='Contenido',
        help_text='Contenido completo de la publicación (LongText en la BD).',
    )
    resumen = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Resumen / Extracto',
        help_text='Breve extracto que aparece en las tarjetas de noticias.',
    )
    imagen_destacada = models.ImageField(
        upload_to='publicaciones/imagenes/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Imagen destacada (archivo)',
    )
    imagen_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Imagen destacada (URL)',
        help_text='URL externa de la imagen. Se usa si no se sube un archivo.',
    )
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de creación',
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización',
    )
    fecha_publicacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de publicación',
    )
    # Relaciones ForeignKey
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='publicaciones',
        verbose_name='Categoría',
    )
    estatus = models.ForeignKey(
        Estatus,
        on_delete=models.PROTECT,
        related_name='publicaciones',
        verbose_name='Estatus',
    )
    autor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='publicaciones',
        verbose_name='Autor',
    )
    vistas = models.PositiveIntegerField(default=0, verbose_name='Vistas')

    class Meta:
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(self.titulo)
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        # Establecer fecha_publicacion cuando se cambia a publicada
        if self.estatus and self.estatus.nombre == Estatus.PUBLICADA:
            if not self.fecha_publicacion:
                self.fecha_publicacion = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:publicacion_detalle', kwargs={'slug': self.slug})

    @property
    def es_publicada(self):
        return self.estatus and self.estatus.nombre == Estatus.PUBLICADA

    @property
    def imagen_src(self):
        """Retorna la URL de la imagen: prioriza el archivo subido, luego la URL externa."""
        if self.imagen_destacada:
            return self.imagen_destacada.url
        if self.imagen_url:
            return self.imagen_url
        return None


# ─────────────────────────────────────────────
#  Archivo (adjunto de publicación)
# ─────────────────────────────────────────────
class Archivo(models.Model):
    """Repositorio de documentos adjuntos relacionados a una publicación."""
    TIPOS = [
        ('pdf', 'PDF'),
        ('word', 'Word (.docx)'),
        ('excel', 'Excel (.xlsx)'),
        ('imagen', 'Imagen'),
        ('otro', 'Otro'),
    ]

    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name='archivos',
        verbose_name='Publicación',
    )
    nombre = models.CharField(max_length=200, verbose_name='Nombre del archivo')
    tipo = models.CharField(
        max_length=10,
        choices=TIPOS,
        default='otro',
        verbose_name='Tipo',
    )
    archivo = models.FileField(
        upload_to='publicaciones/archivos/%Y/%m/',
        verbose_name='Archivo',
    )
    subido_en = models.DateTimeField(auto_now_add=True, verbose_name='Subido el')
    subido_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Subido por',
    )
    tamanio_bytes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Tamaño (bytes)',
    )

    class Meta:
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'
        ordering = ['-subido_en']

    def __str__(self):
        return f"{self.nombre} — {self.publicacion.titulo}"

    def save(self, *args, **kwargs):
        if self.archivo and hasattr(self.archivo, 'size'):
            self.tamanio_bytes = self.archivo.size
        super().save(*args, **kwargs)

    @property
    def tamanio_legible(self):
        """Retorna el tamaño en formato legible (KB, MB)."""
        if not self.tamanio_bytes:
            return 'Desconocido'
        if self.tamanio_bytes < 1024:
            return f"{self.tamanio_bytes} B"
        elif self.tamanio_bytes < 1024 ** 2:
            return f"{self.tamanio_bytes / 1024:.1f} KB"
        return f"{self.tamanio_bytes / (1024 ** 2):.1f} MB"


# ─────────────────────────────────────────────
#  Perfil (extiende User de Django)
# ─────────────────────────────────────────────
class Perfil(models.Model):
    """Extiende el usuario de Django para incluir foto de perfil y rol."""
    ROL_ADMIN = 'admin'
    ROL_EDITOR = 'editor'
    ROL_REDACTOR = 'redactor'
    ROL_LECTOR = 'lector'

    ROLES = [
        (ROL_ADMIN, 'Administrador'),
        (ROL_EDITOR, 'Editor'),
        (ROL_REDACTOR, 'Redactor'),
        (ROL_LECTOR, 'Lector'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario',
    )
    foto_perfil = models.ImageField(
        upload_to='perfiles/%Y/',
        null=True,
        blank=True,
        verbose_name='Foto de perfil',
    )
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default=ROL_LECTOR,
        verbose_name='Rol',
    )
    bio = models.TextField(blank=True, verbose_name='Biografía')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f"Perfil de {self.usuario.get_full_name() or self.usuario.username}"

    @property
    def nombre_completo(self):
        return self.usuario.get_full_name() or self.usuario.username

    @property
    def avatar_url(self):
        if self.foto_perfil:
            return self.foto_perfil.url
        # ─────────────────────────────────────────────
#  Comentario
# ─────────────────────────────────────────────
class Comentario(models.Model):
    """Comentarios de los usuarios en las noticias."""
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADO = 'aprobado'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_APROBADO, 'Aprobado'),
    ]

    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Publicación',
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Usuario',
    )
    usuario_nombre = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name='Nombre del usuario (DB View)',
        help_text='Copia denormalizada del nombre para visualización rápida en BD.'
    )
    texto = models.TextField(verbose_name='Comentario')
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
        verbose_name='Estado',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.publicacion.titulo}"

    def save(self, *args, **kwargs):
        # Guardar el nombre del usuario para facilitar la lectura en la BD
        if self.usuario:
            self.usuario_nombre = self.usuario.get_full_name() or self.usuario.username
        super().save(*args, **kwargs)
