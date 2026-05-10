"""
middleware.py — App 'core'
Middleware de Logs de Actividad HTTP en formato JSON.
Registra cada petición con: método, ruta, IP, user-agent, usuario, status y tiempo de respuesta.
"""

import json
import time
import logging

logger = logging.getLogger('core.activity')


class ActivityLogMiddleware:
    """
    Registra cada petición HTTP entrante en formato JSON.
    Cumple con el requisito de 'Logs de Actividad' de la documentación técnica.
    No registra rutas de archivos estáticos ni de media para reducir ruido.
    """

    RUTAS_IGNORADAS = ('/static/', '/media/', '/favicon.ico')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ignorar rutas de archivos estáticos
        if any(request.path.startswith(ruta) for ruta in self.RUTAS_IGNORADAS):
            return self.get_response(request)

        inicio = time.time()
        response = self.get_response(request)
        duracion_ms = round((time.time() - inicio) * 1000, 2)

        # Determinar usuario
        usuario = 'anonimo'
        if hasattr(request, 'user') and request.user.is_authenticated:
            usuario = request.user.username

        entrada = {
            'metodo': request.method,
            'ruta': request.path,
            'query': request.META.get('QUERY_STRING', ''),
            'status': response.status_code,
            'ip': self._obtener_ip(request),
            'usuario': usuario,
            'duracion_ms': duracion_ms,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:150],
        }

        logger.info(json.dumps(entrada, ensure_ascii=False))
        return response

    @staticmethod
    def _obtener_ip(request):
        """Obtiene la IP real del cliente, considerando proxies."""
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
