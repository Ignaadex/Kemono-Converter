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

def descargar_archivo(url, nombre_archivo):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(nombre_archivo, 'wb') as file:
                file.write(response.content)
            return True
        else:
            print("Error al descargar el archivo:", response.status_code)
            return False
    except Exception as e:
        print("Error al descargar el archivo:", e)
        return False

def extraer_links_m3u8(archivo_txt):
    try:
        with open(archivo_txt, 'r') as file:
            contenido = file.read()
            # Encuentra todos los enlaces M3U8 en el contenido del archivo TXT
            links_m3u8 = re.findall(r'EXT-X-STREAM-INF.*RESOLUTION=1920x1080.*?\n(.*?)\n', contenido)
            return links_m3u8
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
        comando_vlc = f'vlc --no-repeat {archivo_m3u8} --sout="#transcode{{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100}}:standard{{access=file,mux=mp4,dst=output.mp4}}"'
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

            # Extraer enlaces M3U8 del archivo TXT
            links_m3u8 = extraer_links_m3u8(nombre_archivo_txt)
            if links_m3u8:
                # Guardar los enlaces M3U8 en un archivo separado
                nombre_archivo_enlaces = os.path.join(carpeta_enlaces, "enlaces_m3u8.txt")
                guardar_link_en_archivo(links_m3u8, nombre_archivo_enlaces)
                print(f"Enlaces guardados en {nombre_archivo_enlaces}")

                # Convertir cada archivo M3U8 a MP4 y moverlo a la carpeta de videos
                for i, link_m3u8 in enumerate(links_m3u8):
                    nombre_video = f"video_{i}.mp4"
                    archivo_m3u8 = os.path.join(carpeta_enlaces, f"video_{i}.m3u8")
                    descargar_archivo(link_m3u8, archivo_m3u8)
                    convertir_m3u8_a_mp4(archivo_m3u8)
                    os.rename("output.mp4", os.path.join(carpeta_videos, nombre_video))
                    print(f"Video {nombre_video} convertido y movido a la carpeta de videos.")
            else:
                print("No se encontraron enlaces M3U8 en el archivo", nombre_archivo_txt)
        else:
            print("Error al descargar el archivo TXT.")
    else:
        print("No se pudo obtener el enlace al archivo TXT desde", url_pagina_kemono)
