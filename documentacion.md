"Actúa como un desarrollador Senior especializado en Django 5.x. Necesito crear el proyecto web 'Canacintra', enfocado en una sección de noticias avanzada.

1. Configuración de Base de Datos (Crítico):
Ya tengo una base de datos en MySQL. Genera el bloque de configuración para settings.py con estos datos exactos:

NAME: 'canancintra'

USER: 'root'

PASSWORD: 'root'

HOST: 'localhost'

PORT: '3306'

2. Modelos de Datos (App 'core'):
Basándote en el patrón MVT, genera los modelos en models.py:

Publicacion: Título, contenido (LongText), fecha de creación, imagen destacada. Relación ForeignKey con Categoria, Estatus y el modelo User de Django.

Categoria: Nombre y descripción.

Estatus: (Captura, Revisión, Publicada).

Archivo: Repositorio para documentos adjuntos relacionados a una publicación.

Perfil: Extiende el usuario de Django para incluir foto de perfil y un campo de rol.

3. Lógica y Vistas:

Crea un sistema de navegación por categorías (vistas filtradas).

Implementa un buscador de noticias en el encabezado.

Configura el admin.py para que sea muy funcional: incluye filtros laterales por Estatus/Categoría y búsqueda por título.

4. Frontend y Estructura:

Usa herencia de plantillas (base.html).

Implementa el diseño con Bootstrap 5, usando 'cards' modernas para las noticias.

Divide la interfaz usando partials (ej. navbar.html, footer.html) para mantener el código limpio.

5. Bonus Técnico: > Incluye una pequeña función de 'Logs de Actividad' que registre las peticiones HTTP básicas en formato JSON, tal como pide la documentación técnica del proyecto.

Entregables: Dame el código de settings.py (BD), models.py, views.py, y la estructura de index.html."

Portal:  http://127.0.0.1:8000/
Admin:   http://127.0.0.1:8000/admin/
Usuario: admin
Contraseña: [admin1234]