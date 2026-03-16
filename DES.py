import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import re
import tkinter as tk
from tkinter import filedialog

# Configurar tkinter para abrir una ventana de selección de carpeta
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal

# Credenciales de tu aplicación en Spotify Developer
client_id = '802e73917b624d698be118958d54ac34'
client_secret = '600c0ddf646f4456ac8bcab5bfdc4f1e'

# Autenticación usando Client Credentials Flow
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Pedir la URL al usuario
spotify_url = input("Ingresa la URL de la playlist o álbum de Spotify: ").strip()

# Detectar si es playlist o álbum
if "/playlist/" in spotify_url:
    tipo = "playlist"
elif "/album/" in spotify_url:
    tipo = "album"
else:
    raise ValueError("La URL debe ser de una playlist o un álbum de Spotify.")

# Extraer el ID desde la URL
spotify_id = spotify_url.split('/')[-1].split('?')[0]

# Obtener los datos según el tipo
if tipo == "playlist":
    info = sp.playlist(spotify_id)
    nombre = info['name']
    total_tracks = info['tracks']['total']
elif tipo == "album":
    info = sp.album(spotify_id)
    nombre = info['name']
    total_tracks = info['total_tracks']

# Limpiar el nombre para eliminar caracteres no válidos en nombres de archivo
sanitized_name = re.sub(r'[<>:"/\\|?*]', '', nombre)

# Mostrar la cantidad total de canciones
print(f"El {tipo} '{nombre}' tiene un total de {total_tracks} canciones.")

# Abrir ventana de selección de carpeta en Windows
save_path = filedialog.askdirectory(title="Selecciona la carpeta donde deseas guardar el archivo .txt")

if not save_path:
    print("No se seleccionó ninguna carpeta.")
    exit()

# Crear la ruta completa del archivo de texto
file_path = os.path.join(save_path, f"{sanitized_name}.txt")

# Crear o abrir el archivo de texto para escribir los resultados
with open(file_path, 'w', encoding='utf-8') as f:
    # Escribir el número total de canciones al inicio del archivo
    f.write(f"Total de canciones: {total_tracks}\n\n")

    if tipo == "playlist":
        # Iterar sobre todas las canciones de la playlist
        offset = 0
        while offset < total_tracks:
            # Obtener un lote de canciones (máximo 100 canciones por solicitud)
            results = sp.playlist_tracks(spotify_id, offset=offset, limit=100)

            for item in results['items']:
                track = item['track']
                if not track:
                    continue

                artist_name = track['artists'][0]['name']
                track_name = track['name']

                # Formato para escribir en el archivo
                result_line = f'Artista: {artist_name}, Canción: {track_name}\n'

                # Imprimir en consola y escribir en el archivo
                print(result_line, end="")
                f.write(result_line)

            offset += len(results['items'])

    elif tipo == "album":
        # Iterar sobre todas las canciones del álbum
        offset = 0
        while offset < total_tracks:
            # Obtener un lote de canciones del álbum (máximo 50 por solicitud)
            results = sp.album_tracks(spotify_id, offset=offset, limit=50)

            for track in results['items']:
                artist_name = track['artists'][0]['name']
                track_name = track['name']

                # Formato para escribir en el archivo
                result_line = f'Artista: {artist_name}, Canción: {track_name}\n'

                # Imprimir en consola y escribir en el archivo
                print(result_line, end="")
                f.write(result_line)

            offset += len(results['items'])

print(f"Los resultados han sido guardados en '{file_path}'.")