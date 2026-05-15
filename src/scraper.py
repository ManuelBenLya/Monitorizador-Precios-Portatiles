import json
from bs4 import BeautifulSoup
import cloudscraper

def extraer_portatiles(pagina):
    url = f"https://www.pccomponentes.com/portatiles?page={pagina}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    print(f"Conectando a PcComponentes: (pagina {pagina}) {url}...")

    try:
        # Petición limpia con el motor antibots
        scraper = cloudscraper.create_scraper()
        respuesta = scraper.get(url, headers=headers, timeout=15)
        
        if respuesta.status_code != 200:
            print(f"  Error de conexión: {respuesta.status_code}")
            return []

        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # [OPTIMIZADO] Buscamos la etiqueta por id ignorando cualquier otra propiedad de React
        script_datos = soup.find('script', attrs={"id": "microdata-product-list-script"})
        
        if not script_datos or not script_datos.string:
            print(f"  No se localizó el bloque JSON Schema en la página {pagina}.")
            return []
            
        # Parseamos el bloque JSON capturado
        json_data = json.loads(script_datos.string)
        elementos_tienda = json_data.get("itemListElement", [])
        
        lista_portatiles = []
        
        for elemento in elementos_tienda:
            item = elemento.get("item", {})
            oferta = item.get("offers", {})
            
            # Limpieza básica de texto para corregir encodings rotos (ej: 'PortÃ¡til' -> 'Portátil')
            nombre_raw = item.get("name", "")
            nombre_limpio = nombre_raw.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore') if nombre_raw else "Portátil Genérico"
            
            marca_raw = item.get("brand", {}).get("name", "Genérica")
            marca_limpia = marca_raw.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore') if marca_raw else "Genérica"

            datos_finales = {
                "nombre": nombre_limpio,
                "marca": marca_limpia,
                "sku": item.get("sku"),
                "precio": float(oferta.get("price", 0.0)),
                "url": item.get("url")
            }
            
            # Solo guardamos si el producto tiene los datos esenciales correctos
            if datos_finales["nombre"] and datos_finales["precio"] > 0:
                lista_portatiles.append(datos_finales)
            
        return lista_portatiles

    except Exception as e:
        print(f" Error inesperado procesando la página {pagina}: {e}")
        return []

if __name__ == "__main__":
    # Test rápido de ejecución directa
    portatiles = extraer_portatiles(1)
    print(f"\n ¡Éxito! Se han extraído {len(portatiles)} portátiles de la página 1.")
    if portatiles:
        print(f" -> Primer portátil mapeado: {portatiles[0]['nombre']} - {portatiles[0]['precio']}€")