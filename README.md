# Portal de Noticias CANACINTRA

¡Bienvenido al **Portal de Noticias CANACINTRA**! Esta es una plataforma web desarrollada en Python con el framework **Django 5.x** y base de datos **MySQL**, diseñada para la gestión, publicación y visualización de noticias, artículos y comunicados oficiales de la Cámara Nacional de la Industria de Transformación.

---

## 🚀 Características Principales

El proyecto implementa un completo sistema de gestión de contenidos (CMS) estructurado bajo el patrón MVT (Model-View-Template) de Django:

*   **Portada Dinámica:** Sección principal que agrupa las noticias por categorías e incluye un carrusel interactivo con las publicaciones más recientes.
*   **Buscador Avanzado:** Barra de búsqueda en tiempo real (AJAX) para sugerencias instantáneas y una página completa de resultados de búsqueda.
*   **Gestión de Comentarios:** Sistema interactivo donde los usuarios lectores registrados pueden comentar las noticias. Requiere aprobación previa de un editor/administrador para ser visibles públicamente.
*   **Flujo Editorial y Roles:**
    *   **Administrador:** Acceso total al panel de administración y control completo de usuarios, roles, comentarios, categorías e historial.
    *   **Editor:** Puede crear, modificar y publicar noticias propias o de otros redactores. Aprueba y elimina comentarios.
    *   **Redactor:** Puede escribir y editar sus propias publicaciones, pero estas quedan en estado de *Revisión* hasta que un editor o administrador decida publicarlas.
    *   **Lector:** Puede leer noticias, descargar archivos adjuntos y dejar comentarios (sujetos a aprobación).
*   **Panel de Administración Personalizado (Dashboard):** Interfaz fluida basada en AJAX/SPA que permite la gestión completa sin necesidad de recargar la página completa.
*   **Galerías e Imágenes Múltiples:** Soporte para cargar una imagen destacada principal y adjuntar galerías fotográficas adicionales a cada noticia.
*   **Archivos Adjuntos:** Soporte para subir archivos (PDF, Word, Excel, etc.) descargables asociados a cada noticia.
*   **Registro de Actividad (Logging):** Middleware personalizado (`ActivityLogMiddleware`) que registra de forma estructurada todas las peticiones HTTP y actividades en formato JSON dentro de `logs/activity.json`.

---

## 🛠️ Requisitos del Sistema

Para ejecutar este proyecto en tu entorno local, asegúrate de tener instalado:

1.  **Python 3.10** o superior.
2.  **MySQL Server** (se recomienda usar **XAMPP** o **WampServer** para una configuración rápida en Windows).
3.  **Visual Studio Build Tools / Compilador C++** (opcional, requerido en algunos entornos Windows para compilar el conector `mysqlclient`).

---

## ⚙️ Instalación y Configuración paso a paso

Sigue estos pasos detallados para configurar y levantar el proyecto en Windows:

### 1. Clonar o descargar el proyecto
Asegúrate de colocar los archivos del proyecto en un directorio de tu preferencia (ej. `C:\canacintra`).

### 2. Crear y activar un entorno virtual
Abre una terminal (PowerShell o CMD) en la raíz del proyecto y ejecuta:

```powershell
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual (PowerShell)
.\venv\Scripts\Activate.ps1

# Activar el entorno virtual (CMD)
.\venv\Scripts\activate.bat
