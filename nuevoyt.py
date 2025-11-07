import os
import re
import yt_dlp
from tkinter import filedialog, Tk


def sanitize_filename(name: str) -> str:
    """Remove characters not allowed in filenames on Windows/most OSes."""
    return re.sub(r'[<>:"/\\|?*\n\r]+', '', name).strip()

def descargar_audio(busqueda, carpeta_destino, archivo_errores):
    try:
        nombre_archivo = f"{sanitize_filename(busqueda)}.mp3"
        ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

        # Si ya existe y es válido (>1MB), lo omite
        if os.path.exists(ruta_archivo) and os.path.getsize(ruta_archivo) > 1024 * 1024:
            print(f"⏭️ El archivo '{nombre_archivo}' ya existe, se omite la descarga.")
            return

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
            'ignoreerrors': True,
            'quiet': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/120.0.0.0 Safari/537.36'
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']  # fuerza otros métodos
                }
            }
        }

        with yt_dlp.YoutubeDL(opciones) as ydl:
            print(f"🔎 Buscando en YouTube: {busqueda}")
            ydl.download([f"ytsearch1:{busqueda}"])

        # Verificar si el archivo realmente se descargó
        if os.path.exists(ruta_archivo) and os.path.getsize(ruta_archivo) > 1024 * 100:
            print(f"✅ Descargado y convertido: {nombre_archivo}")
        else:
            print(f"❌ No se pudo descargar correctamente: {busqueda}")
            with open(archivo_errores, "a", encoding="utf-8") as f:
                f.write(busqueda + "\n")

    except Exception as e:
        print(f"❌ Error al procesar '{busqueda}': {e}")
        with open(archivo_errores, "a", encoding="utf-8") as f:
            f.write(busqueda + "\n")


if __name__ == "__main__":
    # Pregunta si quieres usar lista TXT o una búsqueda manual
    modo = input("¿Quieres usar un archivo TXT con canciones? (s/n): ").strip().lower()

    # Seleccionar carpeta destino
    Tk().withdraw()
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta donde guardar las descargas")

    if not carpeta:
        print("❌ No se seleccionó carpeta de destino.")
    else:
        archivo_errores = os.path.join(carpeta, "errores.txt")

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
                            descargar_audio(busqueda, carpeta, archivo_errores)
                        except Exception as e:
                            print(f"❌ No se pudo procesar la línea: {linea} - {e}")
            else:
                print("❌ No se seleccionó archivo TXT válido.")
        else:
            consulta = input("Ingresa el nombre del artista y canción: ")
            descargar_audio(consulta, carpeta, archivo_errores)
