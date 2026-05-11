from django.db import connection

def check_tables():
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    
    print(f"{'TABLE NAME':<40} | {'ROWS':<10}")
    print("-" * 55)
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            print(f"{table:<40} | {count:<10}")
        except Exception as e:
            print(f"{table:<40} | ERROR: {e}")

if __name__ == "__main__":
    check_tables()
