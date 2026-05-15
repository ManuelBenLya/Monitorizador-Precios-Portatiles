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
        scraper = cloudscraper.create_scraper()
        respuesta = scraper.get(url, headers=headers, timeout=15)
        
        if respuesta.status_code != 200:
            print(f" Error de conexión: {respuesta.status_code}")
            return []

        # Forzamos a que interprete el texto usando UTF-8 puro para evitar caracteres rotos
        respuesta.encoding = 'utf-8'
        
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Buscamos el script usando un selector flexible por ID
        script_datos = soup.find('script', attrs={"id": "microdata-product-list-script"})
        
        if not script_datos or not script_datos.string:
            print(f" No se encontró la etiqueta de datos en la página {pagina}.")
            return []
            
        # Extraemos el contenido de texto puro del script
        texto_json = script_datos.string.strip()
        
        # Cargamos el bloque de texto como un diccionario de Python
        json_data = json.loads(texto_json)
        elementos_tienda = json_data.get("itemListElement", [])
        
        lista_portatiles = []
        
        for elemento in elementos_tienda:
            item = elemento.get("item", {})
            oferta = item.get("offers", {})
            
            nombre = item.get("name", "")
            marca = item.get("brand", {}).get("name", "Genérica")
            sku = item.get("sku", "")
            precio = float(oferta.get("price", 0.0))
            url_prod = item.get("url", "")
            
            # Limpieza final de strings para arreglar codificaciones extrañas de PcComponentes
            if nombre:
                nombre = nombre.encode('latin1', errors='ignore').decode('utf-8', errors='ignore') if 'Ã' in nombre else nombre
            if brand := item.get("brand", {}).get("name"):
                marca = brand.encode('latin1', errors='ignore').decode('utf-8', errors='ignore') if 'Ã' in brand else brand

            datos_finales = {
                "nombre": nombre,
                "marca": marca,
                "sku": sku,
                "precio": precio,
                "url": url_prod
            }
            
            if datos_finales["nombre"] and datos_finales["precio"] > 0:
                lista_portatiles.append(datos_finales)
                
        return lista_portatiles

    except Exception as e:
        print(f" Error inesperado rascando la página {pagina}: {e}")
        return []

if __name__ == "__main__":
    # Test local para cantar victoria
    portatiles = extraer_portatiles(1)
    print(f"\n ¡EXTRACCIÓN COMPLETADA!")
    print(f" Se han mapeado {len(portatiles)} portátiles reales directos de la estructura.")
    if portatiles:
        print(f" -> Primer portátil detectado: {portatiles[0]['nombre']} - {portatiles[0]['precio']}€")