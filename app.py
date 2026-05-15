import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import obtener_datos_dashboard
from dotenv import load_dotenv  # 👈 Dejas esto para que lea tu archivo .env

load_dotenv()

# Configuración de la página web
st.set_page_config(page_title="Radar de Precios - PcComponentes", page_icon="💻", layout="wide")

st.title(" 💻 Radar de Precios de Portátiles")
st.markdown("Dashboard de ingeniería de datos para el seguimiento de precios en tiempo real.")

# 1. Extracción de datos desde PostgreSQL
try:
    # 🏁 Intento A: Intentamos conectarnos a tu Supabase real
    df = obtener_datos_dashboard() 
    
    if df.empty:
        st.warning("⚠️ Conectado a Supabase, pero las tablas no devuelven registros. ¿Corriste el scraper?")
except Exception as e:
    # 🕵️‍♂️ Si falla el Intento A, te chiva el error en la barra lateral para que sepas qué pasa...
    st.sidebar.error(f"❌ Error de conexión a Supabase: {e}")
    st.sidebar.warning("🔄 Cargando entorno de demostración con datos locales.")
    
    #  Plan B: Datos de prueba por si falla la nube
    df = pd.DataFrame({
        'sku': ['101', '101', '102', '102'],
        'nombre': ['MSI Cyborg 15', 'MSI Cyborg 15', 'ASUS Vivobook', 'ASUS Vivobook'],
        'marca': ['MSI', 'MSI', 'Asus', 'Asus'],
        'precio': [1099.00, 1049.00, 449.00, 429.00],
        'fecha_extraccion': pd.to_datetime(['2026-05-13', '2026-05-15', '2026-05-13', '2026-05-15'])
    })

# 2. Barra Lateral (Filtros)
st.sidebar.header("Filtros del Mercado")
marcas_disponibles = df['marca'].unique()
marcas_seleccionadas = st.sidebar.multiselect("Selecciona Marcas:", options=marcas_disponibles, default=marcas_disponibles)

# Filtrar el DataFrame según la selección del usuario
df_filtrado = df[df['marca'].isin(marcas_seleccionadas)]

# 3. Métricas Clave (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Portátiles Trackeados", len(df_filtrado['sku'].unique()))
with col2:
    st.metric("Precio Medio", f"{round(df_filtrado['precio'].mean(), 2)} €")
with col3:
    # Mostramos la última fecha disponible en el dataset para saber de cuándo son los datos
    if not df_filtrado.empty:
        ultima_fecha = df_filtrado['fecha_extraccion'].max().strftime('%d/%m/%Y')
        st.metric("Última Actualización", ultima_fecha)
    else:
        st.metric("Última Actualización", "Sin datos")

st.markdown("---")

# 4. Gráficos Interactivos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Distribución de Precios por Marca")
    fig_box = px.box(df_filtrado, x="marca", y="precio", color="marca", points="all",
                     title="Rango de Precios por Fabricante")
    st.plotly_chart(fig_box, use_container_width=True)

with col_graf2:
    st.subheader("Evolución Temporal de Precios")
    portatil_elegido = st.selectbox("Elige un modelo para ver su histórico:", df_filtrado['nombre'].unique())
    df_temporal = df_filtrado[df_filtrado['nombre'] == portatil_elegido]
    
    fig_line = px.line(df_temporal, x="fecha_extraccion", y="precio", markers=True,
                       title=f"Historial de: {portatil_elegido}")
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# 5. Vista de los Datos Crudos
st.subheader(" 📋 Inventario de Datos en Tiempo Real")
st.dataframe(df_filtrado, use_container_width=True)