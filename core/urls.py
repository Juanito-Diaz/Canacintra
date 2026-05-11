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
]
