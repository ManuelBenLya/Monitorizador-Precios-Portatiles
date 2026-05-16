import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import obtener_datos_dashboard
from dotenv import load_dotenv 

# Carga forzada de variables de entorno (Local)
load_dotenv()

# Configuración avanzada de la página web (Sintaxis moderna de 2026)
st.set_page_config(
    page_title="Radar de Precios - PcComponentes", 
    page_icon="💻", 
    layout="wide"
)

st.title(" Dashboard de Precios de Portátiles")
st.markdown("Dashboard de ingeniería de datos de alto rendimiento para el seguimiento y monitorización del mercado en tiempo real.")

# ==========================================
# 1. EXTRACCIÓN Y PREPARACIÓN DE DATOS
# ==========================================
try:
    # 🏁 Intento A: Conexión nativa a Supabase
    df_crudo = obtener_datos_dashboard() 
    
    if df_crudo.empty:
        st.warning("⚠️ Conectado a Supabase, pero las tablas no devuelven registros. ¿Corriste el scraper?")
except Exception as e:
    # 🛡️ Plan B: Datos simulados de contingencia (Fallback) por si falla la red
    st.sidebar.error(f"❌ Error de conexión a la BD: {e}")
    st.sidebar.warning("🔄 Cargando entorno de demostración con datos locales simulados.")
    
    df_crudo = pd.DataFrame({
        'sku': ['101', '101', '102', '102', '103', '104', '105'],
        'nombre': [
            'MSI Cyborg 15 A12V', 'MSI Cyborg 15 A12V', 
            'ASUS Vivobook Go 15', 'ASUS Vivobook Go 15',
            'Lenovo IdeaPad Slim 3', 'HP Laptop 15-fc', 'Acer Aspire 3'
        ],
        'marca': ['MSI', 'MSI', 'Asus', 'Asus', 'Lenovo', 'HP', 'Acer'],
        'precio': [1099.00, 1049.00, 449.00, 429.00, 520.00, 610.00, 399.00],
        'url': [
            'https://www.pccomponentes.com', 'https://www.pccomponentes.com',
            'https://www.pccomponentes.com', 'https://www.pccomponentes.com',
            'https://www.pccomponentes.com', 'https://www.pccomponentes.com',
            'https://www.pccomponentes.com'
        ],
        'fecha_extraccion': pd.to_datetime([
            '2026-05-13 10:00:00', '2026-05-16 09:00:00', 
            '2026-05-13 10:00:00', '2026-05-16 09:00:00',
            '2026-05-16 09:00:00', '2026-05-16 09:00:00', '2026-05-16 09:00:00'
        ])
    })

# ==========================================
# 2. LOGICA ANALÍTICA DE PRECIOS RECIENTES
# ==========================================
# Para KPIs, Boxplots y la Tabla final, nos quedamos estrictamente con el ULTIMO precio de cada SKU
df_ultimo = df_crudo.sort_values('fecha_extraccion').groupby('sku').last().reset_index()

# ==========================================
# 3. BARRA LATERAL (FILTROS DE INFRAESTRUCTURA)
# ==========================================
st.sidebar.header("🎯 Filtros del Mercado")

# Filtro A: Selección de Fabricantes
marcas_disponibles = sorted(df_ultimo['marca'].unique())
marcas_seleccionadas = st.sidebar.multiselect(
    "Selecciona Marcas:", 
    options=marcas_disponibles, 
    default=marcas_disponibles
)

# Filtro B: Deslizador dinámico de Presupuesto
precio_min_posible = float(df_ultimo['precio'].min())
precio_max_posible = float(df_ultimo['precio'].max())

# Validación por si el dataset de pruebas es muy pequeño y los precios coinciden
if precio_min_posible == precio_max_posible:
    precio_min_posible -= 10.0
    precio_max_posible += 10.0

rango_precio = st.sidebar.slider(
    "Ajusta tu presupuesto (€):",
    min_value=int(precio_min_posible),
    max_value=int(precio_max_posible),
    value=(int(precio_min_posible), int(precio_max_posible))
)

# Aplicamos los filtros encadenados al Dataset del catálogo actual
df_filtrado_ultimo = df_ultimo[
    (df_ultimo['marca'].isin(marcas_seleccionadas)) & 
    (df_ultimo['precio'] >= rango_precio[0]) & 
    (df_ultimo['precio'] <= rango_precio[1])
]

# ==========================================
# 4. COMPONENTE METRICO (KPIS SUPERIORES)
# ==========================================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Modelos Únicos", len(df_filtrado_ultimo['sku'].unique()))
with col2:
    precio_medio = df_filtrado_ultimo['precio'].mean() if not df_filtrado_ultimo.empty else 0
    st.metric("Precio Medio Catálogo", f"{round(precio_medio, 2)} €")
with col3:
    if not df_filtrado_ultimo.empty:
        ultima_fecha = df_filtrado_ultimo['fecha_extraccion'].max().strftime('%d/%m/%Y %H:%M')
        st.metric("Sincronización Cloud (UTC)", ultima_fecha)
    else:
        st.metric("Sincronización Cloud", "Sin registros")

st.markdown("---")

# ==========================================
# 5. ESTRUCTURA INTERFICIAL DE PESTAÑAS (TABS)
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "📊 Estructura y Cuotas del Mercado", 
    "📈 Historial Cronológico e Índices", 
    "🔥 Detector de Chollos y Bajadas"
])

# ------------------------------------------
# PESTAÑA 1: ANALISIS GLOBAL DE MERCADO
# ------------------------------------------
with tab1:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Distribución de Costes por Fabricante")
        fig_box = px.box(
            df_filtrado_ultimo, x="marca", y="precio", color="marca", points="all",
            title="Dispersión y Rangos de Precios de Portátiles",
            labels={"marca": "Fabricante", "precio": "Precio (€)"}
        )
        fig_box.update_layout(legend_title_text="Marcas")
        st.plotly_chart(fig_box, width='stretch')
        
    with col_g2:
        st.subheader("Cuota de Modelos Expuestos (Stock Share)")
        # Agrupamos para sacar el porcentaje de presencia de cada marca en el catálogo actual
        df_share = df_filtrado_ultimo['marca'].value_counts().reset_index()
        df_share.columns = ['marca', 'cantidad']
        
        fig_pie = px.pie(
            df_share, values='cantidad', names='marca', hole=0.4,
            title="Porcentaje de Variedad de Catálogo por Fabricante"
        )
        st.plotly_chart(fig_pie, width='stretch')

# ------------------------------------------
# PESTAÑA 2: CRONOLOGÍA TEMPORAL POR PRODUCTO
# ------------------------------------------
with tab2:
    st.subheader("Evolución Temporal de Precios de un Modelo")
    
    # Permitimos elegir solo entre los nombres que pasan los filtros actuales de marca/precio
    nombres_disponibles = df_filtrado_ultimo['nombre'].unique()
    
    if len(nombres_disponibles) > 0:
        portatil_elegido = st.selectbox("Busca o selecciona un portátil para ver su evolución:", nombres_disponibles)
        
        # Para la gráfica cronológica cruzamos el nombre elegido con todo el histórico crudo completo
        df_temporal = df_crudo[df_crudo['nombre'] == portatil_elegido].sort_values('fecha_extraccion')
        
        fig_line = px.line(
            df_temporal, x="fecha_extraccion", y="precio", markers=True,
            title=f"Historial de Precios de: {portatil_elegido}",
            labels={"fecha_extraccion": "Fecha del Análisis", "precio": "Precio en Tienda (€)"}
        )
        st.plotly_chart(fig_line, width='stretch')
    else:
        st.info("💡 Mueve los filtros de la barra lateral para ver portátiles disponibles.")

# ------------------------------------------
# PESTAÑA 3: ALGORITMO DETECTOR DE REBAJAS
# ------------------------------------------
with tab3:
    st.subheader("🔥 Top 10 Mayores Descuentos Detectados")
    st.markdown("El sistema analiza de forma automatizada la diferencia entre el coste histórico máximo y el coste actual de cada SKU.")
    
    # 🧠 Lógica inteligente de cálculo de descuentos analizando el histórico crudo entero
    df_max_precios = df_crudo.groupby('sku')['precio'].max().reset_index()
    df_max_precios.columns = ['sku', 'precio_max_historico']
    
    # Fusionamos el precio máximo con los datos de los modelos filtrados actuales
    df_descuentos = pd.merge(df_filtrado_ultimo, df_max_precios, on='sku')
    df_descuentos['descuento_euros'] = df_descuentos['precio_max_historico'] - df_descuentos['precio']
    
    # Filtramos para quedarnos solo con aquellos que de verdad han bajado de precio (> 0 euros)
    df_rebajados = df_descuentos[df_descuentos['descuento_euros'] > 0].sort_values('descuento_euros', ascending=False).head(10)
    
    if not df_rebajados.empty:
        # 1. Pintamos el gráfico de barras limpio (sin la propiedad 'link' rota)
        fig_descuentos = px.bar(
            df_rebajados, x='descuento_euros', y='nombre', orientation='h', color='descuento_euros',
            title="Euros de Descuento respecto a su Máximo Histórico Registrado",
            labels={'descuento_euros': 'Descuento Directo (€)', 'nombre': 'Modelo'},
            color_continuous_scale='oranges'
        )
        fig_descuentos.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_descuentos, width='stretch')
        
        st.markdown("---")
        # 2. 🚀 El truco interactivo: Un Selector de Chollos Directo
        st.subheader("🛒 Enlace Directo a los Chollos del Gráfico")
        st.markdown("Selecciona uno de los portátiles con descuento para abrir su ficha original:")
        
        # Creamos un selector rápido con los nombres del Top 10
        opciones_chollos = df_rebajados['nombre'].unique()
        chollo_seleccionado = st.selectbox("Elige el modelo que te interesa:", opciones_chollos)
        
        # Buscamos los datos exactos (precio, descuento y URL) del modelo que ha pinchado el usuario
        datos_chollo = df_rebajados[df_rebajados['nombre'] == chollo_seleccionado].iloc[0]
        
        # Pintamos un botón interactivo súper llamativo que redirige al usuario
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            st.info(f"✨ **{chollo_seleccionado}**\n\n💰 Precio actual: **{datos_chollo['precio']} €** (¡Has ahorrado **{round(datos_chollo['descuento_euros'], 2)} €** respecto a su precio más alto!)")
        with col_c2:
            st.markdown("<br>", unsafe_allow_html=True) 
            st.link_button("🔥 Ir a por el Chollo en PcComponentes ↗️", datos_chollo['url'], use_container_width=True)
            
    else:
        st.info("📉 No se han registrado variaciones de bajada de precio todavía. El bot necesita acumular más pasadas semanales para contrastar ofertas.")


# ==========================================
# 6. COMPONENTE INTERACTIVO DE DATOS CRUDOS
# ==========================================
st.markdown("---")
st.subheader("📋 Inventario de Datos en Tiempo Real")
st.markdown("Filtra, ordena y busca portátiles de forma dinámica. Haz clic en 'Ir a PcComponentes' para abrir la ficha original del producto.")

# Columnas limpias ordenadas que mostraremos al usuario
columnas_vista = ['sku', 'nombre', 'marca', 'precio', 'fecha_extraccion', 'url']

# Renderizado avanzado de la tabla de datos con enlaces web operativos (LinkColumn)
st.dataframe(
    df_filtrado_ultimo[columnas_vista],
    column_config={
        "url": st.column_config.LinkColumn("Enlace de Compra", display_text="Ir a PcComponentes ↗️"),
        "precio": st.column_config.NumberColumn("Precio Actual", format="%.2f €"),
        "sku": st.column_config.TextColumn("Código SKU"),
        "fecha_extraccion": st.column_config.DatetimeColumn("Última Captura", format="DD/MM/YYYY HH:mm")
    },
    hide_index=True,
    width='stretch'
)