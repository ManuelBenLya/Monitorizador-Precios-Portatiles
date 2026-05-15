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
    
    # PASO 2: Extracción con Cola de Reintentos
    print("\n[2/3] Iniciando la extracción de portátiles con saltos aleatorios...")
    todos_los_productos = [] 
    paginas_fallidas = [] # <-- Aquí guardaremos los 403

    paginas_totales = list(range(1, 88))
    random.shuffle(paginas_totales)

    # --- PRIMERA PASADA ---
    for indice, pagina in enumerate(paginas_totales, start=1):
        if indice > 1 and (indice - 1) % 3 == 0:
            time.sleep(random.uniform(20.0, 35.0))

        time.sleep(random.uniform(10.0, 18.0))
        productos_pagina = extraer_portatiles(pagina)
        
        if productos_pagina:
            todos_los_productos.extend(productos_pagina)
            print(f"    -> Encontrados {len(productos_pagina)} portátiles en página {pagina}.")
        else:
            # [MODIFICADO] Si falla, la anotamos para luego
            print(f"    -> [Cola] Página {pagina} guardada para reintento posterior.")
            paginas_fallidas.append(pagina)

    # --- BUCLE DE REINTENTOS ---
    intentos_maximos = 2  # Para no quedarnos en un bucle infinito si nos banean del todo
    intento_actual = 1

    while paginas_fallidas and intento_actual <= intent_maximos:
        print(f"\n🔄 [REINTENTOS] Iniciando ronda {intento_actual} de páginas fallidas...")
        print(f"⏳ Esperando 60 segundos de reloj para enfriar la IP por completo...")
        time.sleep(60) # Descanso profundo vital antes de volver a la carga
        
        # Volvemos a desordenar las que fallaron
        random.shuffle(paginas_fallidas)
        # Copiamos la lista para iterar y vaciamos la original para la siguiente ronda
        paginas_a_reintentar = list(paginas_fallidas)
        paginas_fallidas = []

        for p_indice, pagina in enumerate(paginas_a_reintentar, start=1):
            time.sleep(random.uniform(8.0, 15.0)) # En los reintentos vamos un pelín más despacio
            
            productos_pagina = extraer_portatiles(pagina)
            if productos_pagina:
                todos_los_productos.extend(productos_pagina)
                print(f"    -> 🔥 ¡REINTENTO EXITOSO! Conseguida página {pagina} ({len(productos_pagina)} productos).")
            else:
                print(f"    -> ❌ Sigue dando 403 la página {pagina}.")
                paginas_fallidas.append(pagina) # Se queda para la ronda 2 si queda margen
                
        intento_actual += 1

    print(f"\n Extracción finalizada. Total acumulado en Supabase: {len(todos_los_productos)} portátiles.")
   # PASO 3: Carga (Almacenamiento e historial de precios)
    print("\n[3/3] Guardando productos e histórico de precios en PostgreSQL...")
    guardar_datos(todos_los_productos)
    
    print("\n=========================================")
    print("   ¡PIPELINE FINALIZADO CON ÉXITO!   ")
    print("=========================================\n")

if __name__ == "__main__":
    ejecutar_pipeline()