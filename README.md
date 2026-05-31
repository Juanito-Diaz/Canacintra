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
```

### 3. Instalar las dependencias
Con el entorno virtual activado, instala las librerías necesarias mediante el archivo [requirements.txt](file:///C:/canacintra/requirements.txt):

```bash
pip install -r requirements.txt
```

> [!NOTE]
> Si tienes problemas instalando `mysqlclient` en Windows, puedes descargar el instalador precompilado (.whl) correspondiente a tu versión de Python desde repositorios oficiales o usar la librería alternativa `PyMySQL`.

### 4. Configurar la Base de Datos en MySQL
1. Inicia tus servicios de **MySQL** y **Apache** en el panel de **XAMPP**.
2. Accede a **phpMyAdmin** (`http://localhost/phpmyadmin/`).
3. Crea una base de datos nueva llamada exactamente:
   ```sql
   canancintra
   ```
   *(Nota: Asegúrate de respetar la ortografía `canancintra`, ya que es la configurada en los settings del proyecto).*
4. El usuario configurado por defecto es `root` con contraseña `root` en el puerto `3306`. Si tu configuración local de XAMPP difiere (por ejemplo, sin contraseña), puedes ajustarla en el archivo [settings.py](file:///C:/canacintra/canacintra_project/settings.py).

### 5. Aplicar Migraciones
Ejecuta las migraciones de Django para crear la estructura de tablas en tu base de datos MySQL:

```bash
python manage.py migrate
```

### 6. Cargar Datos de Prueba (Seeding)
El proyecto incluye un script listo para inicializar la base de datos con categorías, estatus, publicaciones de ejemplo y la cuenta del Administrador principal. Ejecútalo mediante:

```bash
python seed_data.py
```
*(O alternativamente: `python manage.py shell < seed_data.py`)*

### 7. Iniciar el Servidor de Desarrollo
Finalmente, arranca el servidor local de Django:

```bash
python manage.py runserver
```

---

## 🔑 Credenciales de Acceso por Defecto

Una vez que hayas ejecutado el cargador de datos (`seed_data.py`), puedes iniciar sesión con las siguientes credenciales:

*   **Superusuario / Administrador:**
    *   **Usuario:** `admin`
    *   **Contraseña:** `admin1234`
    *   **Email:** `admin@canacintra.mx`

Puedes iniciar sesión directamente en:
*   El Portal de Noticias e interfaz pública: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
*   El Panel de Administración Personalizado: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
*   El Administrador nativo de Django: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 📁 Estructura del Proyecto

A continuación se detalla la distribución de los componentes clave dentro del proyecto:

*   **[canacintra_project/](file:///C:/canacintra/canacintra_project/):** Configuración global de la aplicación Django (URLs principales, WSGI/ASGI y archivo de configuración [settings.py](file:///C:/canacintra/canacintra_project/settings.py)).
*   **[core/](file:///C:/canacintra/core/):** La aplicación principal del negocio. Contiene:
    *   [models.py](file:///C:/canacintra/core/models.py): Modelos de datos para Categorías, Estatus, Publicaciones, Galerías, Archivos, Comentarios y Perfil.
    *   [views.py](file:///C:/canacintra/core/views.py): Lógica de control y renderizado para la sección pública y el panel del dashboard.
    *   [urls.py](file:///C:/canacintra/core/urls.py): Enrutamiento interno del módulo.
    *   [middleware.py](file:///C:/canacintra/core/middleware.py): Lógica del registro de logs HTTP en formato JSON.
*   **[templates/](file:///C:/canacintra/templates/):** Plantillas HTML del proyecto utilizando el motor de plantillas de Django.
*   **[static/](file:///C:/canacintra/static/):** Archivos estáticos del frontend (Hojas de estilo CSS personalizadas, scripts JS para AJAX y librerías externas como Bootstrap).
*   **[media/](file:///C:/canacintra/media/):** Almacenamiento de archivos subidos dinámicamente (imágenes destacadas, fotos de perfil, galerías y adjuntos descargables).
*   **[logs/](file:///C:/canacintra/logs/):** Carpeta donde se guarda el historial de actividad HTTP en JSON.
