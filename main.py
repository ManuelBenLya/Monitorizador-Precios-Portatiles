import os
import sys
import psycopg2
from src.scraper import extraer_portatiles
from src.database import crear_tablas, guardar_datos
import time
import random

def asegurar_base_de_datos_existe():
    """Se conecta a la BD inicial para asegurar la infraestructura tanto en Local como Cloud."""
    try:
        # Usamos 'postgres' como base de datos por defecto para el chequeo inicial
        conexion = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", 5432)),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "datos"),
            dbname="postgres" 
        )
        conexion.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conexion.cursor()
        
        # Leemos qué Base de Datos toca verificar (pccomponentes en local, postgres en Supabase)
        bd_objetivo = os.environ.get("DB_NAME", "pccomponentes")
        
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{bd_objetivo}';")
        existe = cursor.fetchone()
        
        if not existe:
            cursor.execute(f"CREATE DATABASE {bd_objetivo};")
            print(f" Base de datos '{bd_objetivo}' creada con éxito.")
        else:
            print(f" La base de datos '{bd_objetivo}' ya existe. Continuando...")
            
        cursor.close()
        conexion.close()
    except Exception as e:
        print(f" Error crítico de infraestructura: {e}")
        sys.exit(1)

def ejecutar_pipeline():
    print("\n=========================================")
    print("      INICIANDO PIPELINE: PCComponentes       ")
    print("=========================================\n")
    
    # PASO 0: Asegurar la infraestructura en Docker
    asegurar_base_de_datos_existe()
    
    # PASO 1: Asegurar que las tablas de e-commerce existen
    print("\n[1/3] Verificando estructura de tablas...")
    crear_tablas()
    
    # PASO 2: Extracción (El nuevo scraper de JSON)
    print("\n[2/3] Iniciando la extracción de portátiles...")
    todos_los_productos = [] 

    for pagina in range(1, 87):
        #Para evitar DDOS
        espera = random.uniform(1.5, 3.5) # Elige un número aleatorio entre 1.5 y 3.5 segundos
        print(f" Esperando {round(espera, 2)} segundos para no saturar el servidor...")
        time.sleep(espera)
        productos_pagina = extraer_portatiles(pagina)
        
        if productos_pagina:
            # .extend() añade los elementos de la lista directamente a nuestra bolsa principal
            todos_los_productos.extend(productos_pagina)
            print(f"   -> Encontrados {len(productos_pagina)} portátiles en página {pagina}.")
        else:
            # Si una página viene vacía, probablemente hayamos llegado al final del catálogo antes de tiempo
            print(f"   -> Fin del catálogo detectado o página vacía en la iteración {pagina}.")
            break 
            
    print(f"\n Extracción completada. Total acumulado: {len(todos_los_productos)} portátiles.")
    # PASO 3: Carga (Almacenamiento e historial de precios)
    print("\n[3/3] Guardando productos e histórico de precios en PostgreSQL...")
    guardar_datos(todos_los_productos)
    
    print("\n=========================================")
    print("   ¡PIPELINE FINALIZADO CON ÉXITO!   ")
    print("=========================================\n")

if __name__ == "__main__":
    ejecutar_pipeline()