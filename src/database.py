import pandas as pd
import psycopg2
import streamlit as st
from psycopg2.extras import execute_values
import os

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "datos"),
    "dbname": os.environ.get("DB_NAME", "pccomponentes")
}

def conectar_db():
    """Establece la conexión con PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)

def crear_tablas():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS marcas (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) UNIQUE NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS productos (
            sku VARCHAR(50) PRIMARY KEY,
            nombre TEXT NOT NULL,
            url TEXT,
            mar_id INTEGER NOT NULL,
            FOREIGN KEY (mar_id) REFERENCES marcas (id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS historico_precios (
            id SERIAL PRIMARY KEY,
            producto_sku VARCHAR(50) NOT NULL,
            precio NUMERIC(10, 2) NOT NULL,
            fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_sku) REFERENCES productos (sku) ON DELETE CASCADE
        )
        """
    )

    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        # Ejecutamos cada comando SQL
        for command in commands:
            cursor.execute(command)
            
        cursor.close()
        conexion.commit() # Confirmamos los cambios en la BD
        print("¡Tablas creadas con éxito en PostgreSQL!")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al crear las tablas: {error}")
    finally:
        if conexion is not None:
            conexion.close()

def guardar_datos(lista_productos):
    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        for prod in lista_productos:
            # 1. Insertar marca si no existe
            cursor.execute(
                "INSERT INTO marcas (nombre) VALUES (%s) ON CONFLICT (nombre) DO UPDATE SET nombre = EXCLUDED.nombre RETURNING id;",
                (prod['marca'],)
            )
            marca_id = cursor.fetchone()[0]

            # 2. Insertar producto (si ya existe por SKU, actualiza el nombre o URL por si acaso)
            cursor.execute(
                """
                INSERT INTO productos (sku, nombre, url, mar_id) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (sku) DO UPDATE SET nombre = EXCLUDED.nombre, url = EXCLUDED.url
                """,
                (prod['sku'], prod['nombre'], prod['url'], marca_id)
            )

            # 3. Registrar el precio en el histórico (esta tabla SIEMPRE inserta, no tiene ON CONFLICT)
            cursor.execute(
                "INSERT INTO historico_precios (producto_sku, precio) VALUES (%s, %s)",
                (prod['sku'], prod['precio'])
            )
            
        conexion.commit()
        print(f" Se han procesado e insertado {len(lista_productos)} precios en el histórico.")
    except Exception as error:
        print(f"Error al guardar datos: {error}")
        conexion.rollback()
    finally:
        cursor.close()
        conexion.close()

# ... mantén tus funciones de conectar_db, crear_tablas y guardar_datos igual ...

@st.cache_data(ttl=600) 
def obtener_datos_dashboard():
    """Conecta a la BD y devuelve un DataFrame con el histórico de precios optimizado."""
    conexion = conectar_db()
    
    # Hemos optimizado la consulta para asegurarnos de que el dashboard reciba las columnas
    # que espera tu archivo visual (sku, nombre, url, marca, precio, fecha_extraccion)
    query = """
        SELECT 
            p.sku, 
            p.nombre, 
            p.url, 
            m.nombre AS marca, 
            h.precio, 
            h.fecha_extraccion
        FROM productos p
        JOIN marcas m ON p.mar_id = m.id
        JOIN historico_precios h ON p.sku = h.producto_sku
        ORDER BY h.fecha_extraccion DESC;
    """
    
    # Pandas nos permite transformar una consulta SQL directamente en un DataFrame
    df = pd.read_sql_query(query, conexion)
    conexion.close()
    
    # Forzamos a que la columna de fecha sea de tipo datetime de Pandas
    # Esto es vital para que los gráficos temporales de Plotly no se vuelvan locos
    if not df.empty:
        df['fecha_extraccion'] = pd.to_datetime(df['fecha_extraccion'])
        
    return df