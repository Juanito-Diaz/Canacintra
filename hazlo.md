Actúa como un Desarrollador Full-Stack Senior. Genera el código necesario para añadir las siguientes funcionalidades a un proyecto de noticias existente:

1. Estructura de Datos (SQL):
Actualiza la base de datos para incluir las siguientes tablas y campos, utilizando las credenciales: host: localhost, port: 3306, user: root, password: root.

Tabla usuarios: id, nombre, email, password (hash), rol (admin o usuario).

Tabla comentarios: id, id_noticia, id_usuario, texto, estado (ENUM: 'pendiente', 'aprobado'), fecha_creacion.

Tabla noticias: Asegurarse de que exista el campo fecha_publicacion e imagen_url.

2. Lógica del Backend (Node.js/Express):
Crea los endpoints necesarios para:

Autenticación: Login y Registro de usuarios.

Carrusel: Un endpoint GET /noticias/recientes que devuelva únicamente las 5 noticias más actuales (ordenadas por fecha descendente).

Comentarios: * POST /comentarios: El usuario envía un comentario con estado inicial 'pendiente'.

GET /comentarios/:id_noticia: Que devuelva solo los comentarios con estado 'aprobado'.

PATCH /comentarios/aprobar/:id: Endpoint protegido para que el administrador cambie el estado a 'aprobado'.

3. Interfaz de Usuario (React Native):

Pantalla de Inicio: Implementa un componente de Carrusel en la parte superior que consuma las 5 noticias más recientes. Debe incluir indicadores (puntos) y permitir el deslizamiento horizontal.

Sección de Usuario: Pantalla de inicio de sesión y registro con diseño minimalista.

Detalle de Noticia: * Añadir una sección de comentarios al final del contenido.

Mostrar el formulario para comentar solo si el usuario ha iniciado sesión.

Incluir un aviso: "Tu comentario aparecerá una vez que sea revisado por un administrador".

Módulo de Administración: Una vista de "Moderación de Comentarios" que liste los mensajes pendientes con botones para "Aprobar" o "Eliminar".

4. Especificaciones Técnicas:

Usa Axios para todas las peticiones a la API.

Aplica estilos profesionales con StyleSheet (paleta de colores azul y gris, diseño limpio).

Implementa el manejo de estados para actualizar la lista de comentarios tras la aprobación del administrador.