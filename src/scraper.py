import json
import requests
from bs4 import BeautifulSoup

def extraer_portatiles(pagina):
    url = f"https://www.pccomponentes.com/aniversario/portatiles?page={pagina}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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