from django.db import connection

def cleanup():
    cursor = connection.cursor()
    tables_to_drop = ['comentarios', 'usuarios', 'noticias']
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
            print(f"Eliminada tabla: {table}")
        except Exception as e:
            print(f"Error al eliminar {table}: {e}")

if __name__ == "__main__":
    cleanup()
