"""
seed_data.py — Script para cargar datos de ejemplo en CANACINTRA.
Ejecutar con: python manage.py shell < seed_data.py
o directamente: python seed_data.py (desde el directorio del proyecto)
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canacintra_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from core.models import Categoria, Estatus, Publicacion, Perfil

print("🌱 Cargando datos de ejemplo...")

# ── 1. Estatus ──────────────────────────────────────────────
for nombre in [Estatus.CAPTURA, Estatus.REVISION, Estatus.PUBLICADA]:
    Estatus.objects.get_or_create(nombre=nombre)
    print(f"  Estatus '{nombre}' ✓")

# ── 2. Categorías ───────────────────────────────────────────
categorias_data = [
    ("Industria", "Noticias del sector industrial mexicano."),
    ("Economía", "Análisis económico nacional e internacional."),
    ("Tecnología", "Innovación y transformación digital empresarial."),
    ("Legislación", "Marco regulatorio y cambios normativos para la industria."),
    ("Sustentabilidad", "Iniciativas verdes y responsabilidad ambiental."),
]
categorias = {}
for nombre, desc in categorias_data:
    cat, _ = Categoria.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
    categorias[nombre] = cat
    print(f"  Categoría '{nombre}' ✓")

# ── 3. Superusuario ─────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@canacintra.mx',
        password='admin1234',
        first_name='Admin',
        last_name='CANACINTRA',
    )
    print("  Superusuario 'admin' creado ✓  (pass: admin1234)")
else:
    admin = User.objects.get(username='admin')
    print("  Superusuario 'admin' ya existe ✓")

# ── 4. Publicaciones de ejemplo ─────────────────────────────
estatus_pub = Estatus.objects.get(nombre=Estatus.PUBLICADA)

noticias = [
    {
        'titulo': 'CANACINTRA impulsa la transformación digital en el sector manufacturero',
        'resumen': 'La cámara lidera iniciativas para integrar tecnología 4.0 en las líneas de producción industriales.',
        'contenido': '''La Cámara Nacional de la Industria de Transformación (CANACINTRA) anunció hoy un 
ambicioso programa de digitalización dirigido a más de 5,000 empresas manufactureras del país.

El plan incluye talleres de capacitación en automatización, inteligencia artificial aplicada a 
procesos productivos, y acceso a financiamiento preferencial para la adopción de tecnologías 
Industry 4.0.

"La transformación digital no es una opción, es una necesidad para que nuestras empresas sean 
competitivas en los mercados globales", señaló el Director General de CANACINTRA durante la 
presentación del programa.

El programa inicia en el primer trimestre con pilotos en los estados de Nuevo León, Jalisco y 
Ciudad de México.''',
        'categoria': categorias['Tecnología'],
    },
    {
        'titulo': 'Reforma fiscal 2026: impacto en la industria de transformación',
        'resumen': 'Análisis de los principales cambios tributarios y su efecto en la competitividad empresarial.',
        'contenido': '''El paquete fiscal aprobado para el ejercicio 2026 trae cambios significativos para 
el sector industrial. CANACINTRA analiza los puntos críticos que afectarán a las empresas 
manufactureras.

Entre los cambios más relevantes destacan: modificaciones al esquema de deducción de inversiones 
en activo fijo, nuevas reglas de capitalización delgada y ajustes en el régimen de maquila.

El departamento jurídico-fiscal de CANACINTRA estará ofreciendo consultas gratuitas a sus 
afiliados durante el mes de enero para asesorar sobre la correcta aplicación de las nuevas 
disposiciones.''',
        'categoria': categorias['Legislación'],
    },
    {
        'titulo': 'Crecimiento del PIB industrial supera expectativas en primer trimestre',
        'resumen': 'El sector manufacturero registró un crecimiento del 4.2%, impulsado por las exportaciones.',
        'contenido': '''Los datos preliminares del INEGI confirman que el Producto Interno Bruto del sector 
industrial creció 4.2% en términos anuales durante el primer trimestre, superando las proyecciones 
iniciales del 3.1%.

Las exportaciones manufactureras lideraron el crecimiento, especialmente en los sectores 
automotriz, aeroespacial y electrónico. La proximidad geográfica con Estados Unidos y los 
incentivos del T-MEC continúan siendo factores clave.

CANACINTRA celebra estos resultados y reafirma su compromiso de seguir promoviendo condiciones 
favorables para la inversión industrial en México.''',
        'categoria': categorias['Economía'],
    },
    {
        'titulo': 'Programa de certificación ambiental para plantas industriales',
        'resumen': 'Nueva norma voluntaria permite a empresas demostrar su compromiso con el medio ambiente.',
        'contenido': '''CANACINTRA, en colaboración con la SEMARNAT, lanzó el Programa de Certificación 
Ambiental Industrial (PCAI), una norma voluntaria que permite a las plantas industriales 
certificar sus prácticas ambientales.

El programa evalúa criterios como eficiencia energética, gestión de residuos, huella de carbono 
y uso responsable del agua. Las empresas certificadas obtienen beneficios fiscales y acceso 
preferencial a contratos con el sector público.

"La sustentabilidad y la competitividad van de la mano. Las empresas que adoptan prácticas 
verdes reducen costos y mejoran su imagen ante clientes globales", afirmó la coordinadora del 
programa.''',
        'categoria': categorias['Sustentabilidad'],
    },
    {
        'titulo': 'Acuerdo sectorial para el desarrollo de proveedores nacionales',
        'resumen': 'Grandes empresas se comprometen a incrementar compras a proveedores mexicanos.',
        'contenido': '''Un acuerdo histórico fue firmado hoy entre CANACINTRA y las principales empresas 
manufactureras transnacionales instaladas en México, comprometiéndose a incrementar gradualmente 
su compra de insumos y servicios a proveedores nacionales.

El objetivo es alcanzar un contenido nacional del 45% en sus cadenas de suministro para 2028, 
lo que generaría alrededor de 120,000 empleos directos adicionales en la industria de 
transformación.

El programa incluye transferencia de tecnología, certificación de calidad y acceso a crédito 
para que las PyMES mexicanas puedan cumplir con los estándares requeridos por las grandes 
corporaciones.''',
        'categoria': categorias['Industria'],
    },
]

for data in noticias:
    pub, created = Publicacion.objects.get_or_create(
        titulo=data['titulo'],
        defaults={
            'resumen': data['resumen'],
            'contenido': data['contenido'],
            'categoria': data['categoria'],
            'estatus': estatus_pub,
            'autor': admin,
        }
    )
    if created:
        print(f"  Noticia '{data['titulo'][:50]}…' ✓")
    else:
        print(f"  Noticia ya existe: '{data['titulo'][:50]}…'")

print("\n✅ Datos de ejemplo cargados correctamente.")
print("   Accede al admin en: http://127.0.0.1:8000/admin/")
print("   Usuario: admin  |  Contraseña: admin1234")
