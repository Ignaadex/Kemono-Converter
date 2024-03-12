'''
Created by Ignacio
12/03/24
'''

import os
import requests
import re
import subprocess

def obtener_enlace_archivo_txt(url_pagina):
    try:
        response = requests.get(url_pagina)
        if response.status_code == 200:
            # Busca el enlace al archivo TXT en la página
            enlace_archivo = re.search(r'href="([^"]+\.txt)"', response.text)
            if enlace_archivo:
                return enlace_archivo.group(1)
            else:
                print("No se encontró el enlace al archivo TXT.")
                return None
        else:
            print("Error al obtener la página:", response.status_code)
            return None
    except Exception as e:
        print("Error al obtener el enlace al archivo TXT:", e)
        return None

session = requests.Session()

def descargar_archivo(url, nombre_archivo):
    try:
        with session.get(url, stream=True) as response:
            response.raise_for_status()
            with open(nombre_archivo, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True
    except requests.HTTPError as e:
        print(f"Error al descargar el archivo: {e}")
        return False

def extraer_links_m3u8(archivo_txt):
    try:
        with open(archivo_txt, 'r') as file:
            contenido = file.read()
            # Encuentra todos los enlaces M3U8 en el contenido del archivo TXT
            matches = re.findall(r'EXT-X-STREAM-INF.*RESOLUTION=(\d+x\d+).*?\n(.*?)\n', contenido)
            return [(resolucion, link) for resolucion, link in matches]
    except Exception as e:
        print("Error al extraer los enlaces M3U8:", e)
        return []

def guardar_link_en_archivo(links_m3u8, nombre_archivo):
    try:
        with open(nombre_archivo, 'w') as file:
            for link in links_m3u8:
                file.write(link + '\n')
        print("Enlaces guardados en", nombre_archivo)
    except Exception as e:
        print("Error al guardar los enlaces en el archivo:", e)

def convertir_m3u8_a_mp4(archivo_m3u8):
    try:
        comando_vlc = f'vlc --no-repeat {archivo_m3u8} --sout="#transcode{{vcodec=h265,acodec=mpga,ab=128,channels=2,samplerate=44100}}:standard{{access=file,mux=mp4,dst=output.mp4}}"'
        subprocess.run(comando_vlc, shell=True, check=True)
        print("Conversión completada.")
    except Exception as e:
        print("Error al convertir el archivo M3U8 a MP4:", e)

if __name__ == "__main__":
    # Solicitar al usuario el enlace del post
    url_pagina_kemono = input("Por favor, introduce el enlace del post en Kemono: ")

    # Obtener el enlace al archivo TXT desde la página
    enlace_archivo_txt = obtener_enlace_archivo_txt(url_pagina_kemono)

    if enlace_archivo_txt:
        print("Enlace al archivo TXT encontrado:", enlace_archivo_txt)

        # Descargar el archivo TXT
        nombre_archivo_txt = input("Por favor, introduce el nombre para el archivo TXT: ")
        if descargar_archivo(enlace_archivo_txt, nombre_archivo_txt):
            print("Archivo TXT descargado correctamente.")

            # Crear una carpeta para los enlaces M3U8 y videos
            carpeta_enlaces = "enlaces_m3u8"
            carpeta_videos = "videos"
            os.makedirs(carpeta_enlaces, exist_ok=True)
            os.makedirs(carpeta_videos, exist_ok=True)

            # Extraer enlaces M3U8 y sus resoluciones del archivo TXT
            links_m3u8 = extraer_links_m3u8(nombre_archivo_txt)
            if links_m3u8:
                print("Resoluciones disponibles:")
                for i, (resolucion, _) in enumerate(links_m3u8):
                    print(f"{i + 1}. {resolucion}")

                # Permitir al usuario elegir la resolución
                seleccion = int(input("Selecciona la resolución que deseas procesar (ingresa el número): ")) - 1
                resolucion_elegida, link_elegido = links_m3u8[seleccion]

                print(f"Resolución seleccionada: {resolucion_elegida}")

                # Guardar el enlace M3U8 en un archivo separado
                nombre_archivo_enlaces = os.path.join(carpeta_enlaces, f"enlaces_m3u8_{resolucion_elegida.replace('x', '_')}.txt")
                guardar_link_en_archivo([link_elegido], nombre_archivo_enlaces)
                print(f"Enlaces guardados en {nombre_archivo_enlaces}")

                # Convertir el archivo M3U8 a MP4
                convertir_m3u8_a_mp4(nombre_archivo_enlaces)
            else:
                print("No se encontraron enlaces M3U8 en el archivo", nombre_archivo_txt)
        else:
            print("Error al descargar el archivo TXT.")
    else:
        print("No se pudo obtener el enlace al archivo TXT desde", url_pagina_kemono)
