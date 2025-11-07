import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import re  # Para limpiar caracteres no válidos
import tkinter as tk
from tkinter import filedialog

# Configurar tkinter para abrir una ventana de selección de carpeta
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal

# Credenciales de tu aplicación en Spotify Developer
client_id = '2483a4dbfbf04ce4bd726cdd1e628495'
client_secret = '89d71a33ef08452e87ffcf22bfd59ba3'

# Autenticación usando Client Credentials Flow
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Pedir la URL de la playlist al usuario
playlist_url = input("Ingresa la URL de la playlist de Spotify: ")

# Extraer el ID de la playlist desde la URL
playlist_id = playlist_url.split('/')[-1].split('?')[0]

# Obtener los datos de la playlist
playlist_info = sp.playlist(playlist_id)
playlist_name = playlist_info['name']
total_tracks = playlist_info['tracks']['total']

# Limpiar el nombre de la playlist para eliminar caracteres no válidos en nombres de archivo
sanitized_playlist_name = re.sub(r'[<>:"/\\|?*]', '', playlist_name)

# Mostrar la cantidad total de canciones
print(f"La playlist '{playlist_name}' tiene un total de {total_tracks} canciones.")

# Abrir ventana de selección de carpeta en Windows
save_path = filedialog.askdirectory(title="Selecciona la carpeta donde deseas guardar el archivo .txt")

# Crear la ruta completa del archivo de texto
file_path = os.path.join(save_path, f"{sanitized_playlist_name}.txt")

# Crear o abrir el archivo de texto para escribir los resultados
with open(file_path, 'w', encoding='utf-8') as f:
    # Escribir el número total de canciones al inicio del archivo
    f.write(f"Total de canciones: {total_tracks}\n\n")
    
    # Iterar sobre todas las canciones de la playlist
    offset = 0
    while offset < total_tracks:
        # Obtener un lote de canciones (máximo 100 canciones por solicitud)
        results = sp.playlist_tracks(playlist_id, offset=offset)
        
        for item in results['items']:
            track = item['track']
            artist_name = track['artists'][0]['name']
            track_name = track['name']
            
            # Formato para escribir en el archivo (sin enumeración)
            result_line = f'Artista: {artist_name}, Canción: {track_name}\n'
            
            # Imprimir en consola y escribir en el archivo
            print(result_line)
            f.write(result_line)

        # Incrementar el offset para obtener el siguiente lote de canciones
        offset += len(results['items'])

print(f"Los resultados han sido guardados en '{file_path}'.")
