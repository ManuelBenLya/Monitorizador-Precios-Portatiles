import psycopg2


DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "datos"),
    "dbname": os.environ.get("DB_NAME", "pccomponentes")
}

try:
    print("Intentando conectar a Supabase desde el entorno virtual...")
    conn = psycopg2.connect(**DB_CONFIG)
    print("¡CONEXIÓN EXITOSA CON LA NUBE! ")
    conn.close()
except Exception as e:
    print(f" Error de conexión todavía: {e}")