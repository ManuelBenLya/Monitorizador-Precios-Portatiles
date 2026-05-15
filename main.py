import sys
import psycopg2
from src.scraper import extraer_portatiles
from src.database import crear_tablas, guardar_datos
import time
import random

def asegurar_base_de_datos_existe():
    # Nos conectamos a la BD por defecto ('postgres') para poder crear la nueva
    conexion = psycopg2.connect(
        host="localhost", port=5432, user="postgres", password="datos", dbname="postgres"
    )
    # En PostgreSQL, la creación de BD no puede ejecutarse dentro de una transacción activa
    conexion.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conexion.cursor()
    
    # Comprobamos si ya existe la BD 'pccomponentes'
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'pccomponentes';")
    existe = cursor.fetchone()
    
    if not existe:
        cursor.execute("CREATE DATABASE pccomponentes;")
        print("💾 Base de datos 'pccomponentes' creada desde cero.")
    else:
        print("🔍 Base de datos 'pccomponentes' ya existía.")
        
    cursor.close()
    conexion.close()

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

    for pagina in range(1, 30):
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