import psycopg2

DB_CONFIG = {
    "host": "aws-1-eu-central-1.pooler.supabase.com", 
    "port": 5432,
    "user": "postgres.opxwwbhrxfmftvvqassx",
    "password": "fqkX2RoLZcRjiIRT", 
    "dbname": "postgres"
}

try:
    print("Intentando conectar a Supabase desde el entorno virtual...")
    conn = psycopg2.connect(**DB_CONFIG)
    print("¡CONEXIÓN EXITOSA CON LA NUBE! ")
    conn.close()
except Exception as e:
    print(f" Error de conexión todavía: {e}")