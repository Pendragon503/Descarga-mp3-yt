import os
import re
import yt_dlp
from tkinter import filedialog, Tk


def sanitize_filename(name: str) -> str:
    """Remove characters not allowed in filenames on Windows/most OSes."""
    return re.sub(r'[<>:"/\\|?*\n\r]+', '', name).strip()

def descargar_audio(busqueda, carpeta_destino):
    try:
        # Nombre final del archivo
        nombre_archivo = f"{sanitize_filename(busqueda)}.mp3"
        ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

        # Si ya existe, no lo descarga
        if os.path.exists(ruta_archivo):
            print(f"⏭️ El archivo '{nombre_archivo}' ya existe, se omite la descarga.")
            return

        # Configuración de descarga con conversión a mp3
        opciones = {
            'format': 'bestaudio/best',
            'outtmpl': ruta_archivo.replace("\\", "/").replace(".mp3", ".%(ext)s"),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
            'noplaylist': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(opciones) as ydl:
            print(f"🔎 Buscando en YouTube: {busqueda}")
            ydl.download([f"ytsearch1:{busqueda}"])  # busca el primer resultado

        print(f"✅ Descargado y convertido: {nombre_archivo}")

    except Exception as e:
        print(f"❌ Error al procesar '{busqueda}': {e}")


if __name__ == "__main__":
    # Pregunta si quieres usar lista TXT o una búsqueda manual
    modo = input("¿Quieres usar un archivo TXT con canciones? (s/n): ").strip().lower()

    # Seleccionar carpeta destino
    Tk().withdraw()
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta donde guardar las descargas")

    if not carpeta:
        print("❌ No se seleccionó carpeta de destino.")
    else:
        if modo == "s":
            # Seleccionar archivo TXT
            ruta_txt = filedialog.askopenfilename(
                title="Selecciona el archivo TXT con las canciones",
                filetypes=[("Archivos de texto", "*.txt")]
            )

            if ruta_txt and os.path.exists(ruta_txt):
                with open(ruta_txt, "r", encoding="utf-8") as f:
                    lineas = f.readlines()

                for linea in lineas:
                    if linea.strip().startswith("Artista:"):
                        try:
                            # Extraer "Artista: X, Canción: Y"
                            partes = linea.strip().replace("Artista:", "").split(", Canción:")
                            artista = partes[0].strip()
                            cancion = partes[1].strip()
                            busqueda = f"{artista} {cancion}"
                            descargar_audio(busqueda, carpeta)
                        except Exception as e:
                            print(f"❌ No se pudo procesar la línea: {linea} - {e}")
            else:
                print("❌ No se seleccionó archivo TXT válido.")
        else:
            consulta = input("Ingresa el nombre del artista y canción: ")
            descargar_audio(consulta, carpeta)
