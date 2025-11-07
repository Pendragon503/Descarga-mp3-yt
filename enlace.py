import os
import yt_dlp
from tkinter import filedialog, Tk

def descargar_audio(url_video, carpeta_destino, archivo_errores):
    try:
        # Nombre base del archivo (usa el ID o título del video)
        opciones_info = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(opciones_info) as ydl:
            info = ydl.extract_info(url_video, download=False)
            titulo = info.get('title', 'audio_descargado')
        nombre_archivo = f"{titulo}.mp3"
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
                    'player_client': ['android', 'web']
                }
            }
        }

        with yt_dlp.YoutubeDL(opciones) as ydl:
            print(f"🎵 Descargando audio desde: {url_video}")
            ydl.download([url_video])

        if os.path.exists(ruta_archivo) and os.path.getsize(ruta_archivo) > 1024 * 100:
            print(f"✅ Descargado y convertido: {nombre_archivo}")
        else:
            print(f"❌ No se pudo descargar correctamente: {url_video}")
            with open(archivo_errores, "a", encoding="utf-8") as f:
                f.write(url_video + "\n")

    except Exception as e:
        print(f"❌ Error al procesar '{url_video}': {e}")
        with open(archivo_errores, "a", encoding="utf-8") as f:
            f.write(url_video + "\n")


if __name__ == "__main__":
    # Pedir enlace del video de YouTube
    url = input("🔗 Ingresa el enlace del video de YouTube: ").strip()

    if not url:
        print("❌ No se ingresó ningún enlace.")
    else:
        # Seleccionar carpeta destino
        Tk().withdraw()
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta donde guardar el audio")

        if not carpeta:
            print("❌ No se seleccionó carpeta de destino.")
        else:
            archivo_errores = os.path.join(carpeta, "errores.txt")
            descargar_audio(url, carpeta, archivo_errores)
