import os
from tkinter import Tk, filedialog, messagebox
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

def leer_playlist(file_path):
    canciones = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                # Formato esperado: Canción - Artista - Álbum
                partes = line.split(" - ")
                if len(partes) == 3:
                    titulo, artista, album = partes
                elif len(partes) == 2:
                    titulo, artista = partes
                    album = "Desconocido"
                else:
                    titulo = line
                    artista = "Desconocido"
                    album = "Desconocido"
                canciones.append((titulo, artista, album))
    return canciones

def asignar_tags(music_folder, canciones):
    archivos = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]
    archivos.sort()  # asegura el mismo orden que playlist.txt
    for idx, archivo in enumerate(archivos):
        if idx < len(canciones):
            titulo, artista, album = canciones[idx]
            mp3_path = os.path.join(music_folder, archivo)
            try:
                audio = EasyID3(mp3_path)
            except ID3NoHeaderError:
                # No tiene cabecera ID3; crear etiquetas vacías y guardarlas
                audio = EasyID3()
                try:
                    audio.save(mp3_path)
                except Exception:
                    # Si no puede guardar ahora, seguirá y guardará al final
                    pass
            except Exception as e:
                print(f"❌ Error al abrir '{mp3_path}': {e}")
                audio = EasyID3()
            audio["title"] = titulo
            audio["artist"] = artista
            audio["album"] = album
            audio["tracknumber"] = str(idx + 1)
            audio.save(mp3_path)
            print(f"✅ {archivo} -> {titulo} | {artista} | {album}")
        else:
            print(f"⚠ No hay datos en playlist.txt para: {archivo}")

if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # oculta ventana principal

    # Seleccionar archivo playlist.txt
    txt_file = filedialog.askopenfilename(
        title="Selecciona el archivo playlist.txt",
        filetypes=[("Text files", "*.txt")]
    )

    if not txt_file:
        messagebox.showerror("Error", "No seleccionaste ningún archivo de texto.")
        exit()

    # Seleccionar carpeta de música
    music_folder = filedialog.askdirectory(
        title="Selecciona la carpeta con los MP3"
    )

    if not music_folder:
        messagebox.showerror("Error", "No seleccionaste ninguna carpeta de música.")
        exit()

    canciones = leer_playlist(txt_file)
    asignar_tags(music_folder, canciones)
    messagebox.showinfo("Completado", "✅ Se actualizaron los metadatos de los MP3.")
