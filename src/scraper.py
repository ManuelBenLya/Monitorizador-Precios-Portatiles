import json
import requests
from bs4 import BeautifulSoup

def extraer_portatiles(pagina):
    url = f"https://www.pccomponentes.com/portatiles?page={pagina}"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}
    
    print(f"Conectando a PcComponentes: (pagina {pagina}) {url}...")
    respuesta = requests.get(url, headers=headers)
    
    if respuesta.status_code != 200:
        print(f" Error de conexión: {respuesta.status_code}")
        return []
        
    soup = BeautifulSoup(respuesta.text, 'html.parser')
    
    # Buscamos la etiqueta script que contiene los datos de producto estructurados en formato Schema.org
    script_datos = soup.find('script', id='microdata-product-list-script')
    
    if not script_datos:
        print("No se encontró el script de datos estructurados. El HTML podría haber cambiado.")
        return []
        
    # Cargamos el texto del script como un diccionario de Python
    json_data = json.loads(script_datos.string)
    
    # Navegamos por la estructura del JSON para llegar a los artículos
    elementos_tienda = json_data.get("itemListElement", [])
    
    lista_portatiles = []
    
    for elemento in elementos_tienda:
        item = elemento.get("item", {})
        oferta = item.get("offers", {})
        
        # Extraemos y limpiamos solo la información que nos interesa
        datos_finales = {
            "nombre": item.get("name"),
            "marca": item.get("brand", {}).get("name"),
            "sku": item.get("sku"),
            "precio": float(oferta.get("price", 0)),
            "url": item.get("url")
        }
        
        lista_portatiles.append(datos_finales)
        
    return lista_portatiles

if __name__ == "__main__":
    portatiles = extraer_portatiles()
    print(f"\n¡Éxito! Se han extraído {len(portatiles)} portátiles.")
    if portatiles:
        print(f"Primer portátil detectado: {portatiles[0]['nombre']} - {portatiles[0]['precio']}€")