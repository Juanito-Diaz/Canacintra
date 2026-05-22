"""
urls.py — App 'core'
Rutas del portal de noticias CANACINTRA.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    # Portada / listado de noticias
    path('', views.index, name='index'),

    # Detalle de publicación
    path('noticia/<slug:slug>/', views.publicacion_detalle, name='publicacion_detalle'),

    # Categorías (navegación filtrada)
    path('categoria/<slug:slug>/', views.categoria_detalle, name='categoria_detalle'),

    # Buscador de noticias (página de resultados)
    path('buscar/', views.buscar, name='buscar'),

    # Endpoint AJAX para autocompletado
    path('api/buscar/', views.buscar_ajax, name='buscar_ajax'),

    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:index'), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('accounts/profile/', views.login_redirect, name='login_redirect'),

    # Dashboard / Admin Front-End Custom routes
    path('dashboard/', views.admin_perfil, name='admin_dashboard_root'),
    path('dashboard/perfil/', views.admin_perfil, name='admin_perfil'),
    path('dashboard/noticias/', views.admin_noticias, name='admin_noticias'),
    path('dashboard/noticias/crear/', views.admin_noticia_crear, name='admin_noticia_crear'),
    path('dashboard/noticias/editar/<int:pk>/', views.admin_noticia_editar, name='admin_noticia_editar'),
    path('dashboard/noticias/eliminar/<int:pk>/', views.admin_noticia_eliminar, name='admin_noticia_eliminar'),
    path('dashboard/comentarios/', views.admin_comentarios, name='admin_comentarios'),
    path('dashboard/comentarios/eliminar/<int:pk>/', views.admin_comentario_eliminar, name='admin_comentario_eliminar'),
    path('dashboard/comentarios/aprobar/<int:pk>/', views.admin_comentario_aprobar, name='admin_comentario_aprobar'),
    path('dashboard/categorias/', views.admin_categorias, name='admin_categorias'),
    path('dashboard/categorias/crear/', views.admin_categoria_crear, name='admin_categoria_crear'),
    path('dashboard/categorias/eliminar/<int:pk>/', views.admin_categoria_eliminar, name='admin_categoria_eliminar'),
    path('dashboard/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('dashboard/usuarios/crear/', views.admin_usuario_crear, name='admin_usuario_crear'),
    path('dashboard/usuarios/eliminar/<int:pk>/', views.admin_usuario_eliminar, name='admin_usuario_eliminar'),
    path('dashboard/cambiar-contrasena/', views.admin_cambiar_contrasena, name='admin_cambiar_contrasena'),
]
