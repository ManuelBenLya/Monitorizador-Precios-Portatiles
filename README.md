# Dashboard de Precios de Portátiles

> Aplicación web interactiva para el seguimiento, análisis y visualización en tiempo real de precios de ordenadores portátiles en PCComponentes.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)
![Web%20Scraping](https://img.shields.io/badge/Tech-Web%20Scraping-green.svg)
![License](https://img.shields.io/badge/Licencia-MIT-brightgreen.svg)

---

### ⚠️ Aviso de Uso Educativo y Ético (Disclaimer)
*Este proyecto ha sido desarrollado con fines estrictamente académicos, educativos y como demostración técnica de habilidades en ciencia de datos y desarrollo de software. No persigue ningún fin comercial ni lucrativo. La extracción de datos se realiza respetando la estabilidad de la plataforma de origen mediante accesos espaciados y controlados. Todos los derechos, marcas comerciales y nombres de productos pertenecen exclusivamente a sus respectivos propietarios.*

---

## 📋 Descripción del Proyecto

El mercado tecnológico sufre constantes fluctuaciones de precios debido a ofertas temporales, cambios de stock o lanzamientos. Esto hace que para un usuario común sea difícil saber si un descuento es real o un precio inflado.

**Este Dashboard** es una solución interactiva que automatiza la extracción de datos de ordenadores portátiles, procesa la información y la presenta en un panel de control limpio e intuitivo. La herramienta permite segmentar portátiles según sus especificaciones de hardware y analizar las tendencias del mercado para tomar decisiones de compra inteligentes y basadas en datos.

## ✨ Características Principales

* **Extracción Automatizada (Web Scraping):** Recolección estructurada de datos técnicos esenciales (procesador, memoria RAM, almacenamiento, tarjeta gráfica, estado del producto) y precios de venta actuales.
* **Filtros Avanzados Interactivos:** Segmentación dinámica en tiempo real por marca, rangos de precio, modelo.
* **Visualizaciones Dinámicas:** Gráficos intuitivos para comprender la distribución de los precios en el mercado, las marcas más competitivas y la relación calidad-precio.
* **Detección de Mínimos:** Algoritmo que destaca aquellos equipos que se encuentran en su precio óptimo o presentan caídas significativas de valor en la plataforma analizada.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Interfaz de Usuario:** [Streamlit](https://streamlit.io/) (Framework ágil para desarrollo de aplicaciones de datos).
* **Extracción de Datos:** Beautiful Soup 4 / Requests (Manejo estructurado del HTML y peticiones HTTP).
* **Procesamiento de Datos:** Pandas y NumPy (Para la limpieza de strings, parseo de especificaciones de hardware y estructuración de matrices de datos).
* **Visualización:** Plotly / Altair (Gráficos interactivos fluidos).

## 📂 Estructura del Repositorio

```text
├── data/                   # Archivos históricos almacenados (CSV/JSON)
├── scrapers/               # Scripts y módulos encargados del web scraping
│   └── pcc_scraper.py      # Módulo extractor específico para PCComponentes
├── app.py                  # Archivo principal de la aplicación Streamlit
├── utils.py                # Funciones auxiliares (limpieza de datos, cálculos)
├── requirements.txt        # Dependencias y librerías necesarias para el proyecto
└── README.md               # Documentación del proyecto
Comprar un portátil hoy en día es confuso; los precios fluctúan constantemente en distintas tiendas y es difícil saber si estás ante una oferta real o un precio inflado. Para resolver esto, creé este Monitorizador de Precios de Portátiles en tiempo real utilizando Python y Streamlit.

El mayor reto fue estructurar el web scraping para que no fuera bloqueado, limpiar los datos de las distintas tiendas, automatizar la actualización de los precios, etc.