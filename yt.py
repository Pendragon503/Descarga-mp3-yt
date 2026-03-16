import os
import re
import yt_dlp
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import threading


def sanitize_filename(name: str) -> str:
    """Remove characters not allowed in filenames on Windows/most OSes."""
    return re.sub(r'[<>:"/\\|?*\n\r]+', '', name).strip()

def descargar_audio(busqueda_o_url, carpeta_destino, log_callback):
    try:
        # Detectar si es una URL
        es_url = busqueda_o_url.startswith(('http://', 'https://'))
        
        # Detectar si es una playlist de YouTube
        es_playlist = es_url and 'list=' in busqueda_o_url
        
        # Configuración de descarga con conversión a mp3
        opciones = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(carpeta_destino, "%(title)s.%(ext)s").replace("\\", "/"),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
            'noplaylist': not es_playlist,  # Permitir playlists si es una
            'quiet': False,  # Mostrar progreso
            'progress_hooks': [lambda d: log_callback(f"Progreso: {d['status']} - {d.get('filename', '')}")]
        }

        with yt_dlp.YoutubeDL(opciones) as ydl:
            if es_url:
                log_callback(f"🔎 Descargando desde URL: {busqueda_o_url}")
                ydl.download([busqueda_o_url])
            else:
                log_callback(f"🔎 Buscando en YouTube: {busqueda_o_url}")
                ydl.download([f"ytsearch1:{busqueda_o_url}"])  # busca el primer resultado

        log_callback(f"✅ Descarga completada.")

    except Exception as e:
        log_callback(f"❌ Error al procesar '{busqueda_o_url}': {e}")


class DescargadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de MP3 de YouTube")
        self.root.geometry("600x500")

        # Variables
        self.modo = tk.StringVar(value="manual")
        self.carpeta_destino = ""
        self.archivo_txt = ""

        # Widgets
        ttk.Label(root, text="Modo de descarga:").pack(pady=5)
        frame_modo = ttk.Frame(root)
        frame_modo.pack(pady=5)
        ttk.Radiobutton(frame_modo, text="Manual (URL o búsqueda)", variable=self.modo, value="manual").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(frame_modo, text="Desde archivo TXT", variable=self.modo, value="txt").pack(side=tk.LEFT, padx=10)

        ttk.Label(root, text="Carpeta de destino:").pack(pady=5)
        frame_carpeta = ttk.Frame(root)
        frame_carpeta.pack(pady=5)
        self.lbl_carpeta = ttk.Label(frame_carpeta, text="No seleccionada")
        self.lbl_carpeta.pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_carpeta, text="Seleccionar", command=self.seleccionar_carpeta).pack(side=tk.LEFT)

        self.frame_manual = ttk.Frame(root)
        ttk.Label(self.frame_manual, text="Ingresa URL de YouTube (video o playlist) o búsqueda:").pack(pady=5)
        self.entry_busqueda = ttk.Entry(self.frame_manual, width=50)
        self.entry_busqueda.pack(pady=5)

        self.frame_txt = ttk.Frame(root)
        ttk.Label(self.frame_txt, text="Archivo TXT:").pack(pady=5)
        frame_txt_sel = ttk.Frame(self.frame_txt)
        frame_txt_sel.pack(pady=5)
        self.lbl_txt = ttk.Label(frame_txt_sel, text="No seleccionado")
        self.lbl_txt.pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_txt_sel, text="Seleccionar", command=self.seleccionar_txt).pack(side=tk.LEFT)

        ttk.Button(root, text="Iniciar Descarga", command=self.iniciar_descarga).pack(pady=10)

        self.log_text = scrolledtext.ScrolledText(root, height=15, wrap=tk.WORD)
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)

        self.modo.trace("w", self.cambiar_modo)
        self.cambiar_modo()

    def cambiar_modo(self, *args):
        if self.modo.get() == "manual":
            self.frame_txt.pack_forget()
            self.frame_manual.pack()
        else:
            self.frame_manual.pack_forget()
            self.frame_txt.pack()

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta donde guardar las descargas")
        if carpeta:
            self.carpeta_destino = carpeta
            self.lbl_carpeta.config(text=carpeta)

    def seleccionar_txt(self):
        archivo = filedialog.askopenfilename(title="Selecciona el archivo TXT", filetypes=[("Archivos de texto", "*.txt")])
        if archivo:
            self.archivo_txt = archivo
            self.lbl_txt.config(text=archivo)

    def log(self, mensaje):
        self.log_text.insert(tk.END, mensaje + "\n")
        self.log_text.see(tk.END)

    def iniciar_descarga(self):
        if not self.carpeta_destino:
            messagebox.showerror("Error", "Selecciona una carpeta de destino.")
            return

        if self.modo.get() == "manual":
            busqueda = self.entry_busqueda.get().strip()
            if not busqueda:
                messagebox.showerror("Error", "Ingresa una URL o búsqueda.")
                return
            threading.Thread(target=self.descargar_manual, args=(busqueda,)).start()
        else:
            if not self.archivo_txt:
                messagebox.showerror("Error", "Selecciona un archivo TXT.")
                return
            threading.Thread(target=self.descargar_txt).start()

    def descargar_manual(self, busqueda):
        descargar_audio(busqueda, self.carpeta_destino, self.log)

    def descargar_txt(self):
        try:
            with open(self.archivo_txt, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            for linea in lineas:
                linea = linea.strip()
                if linea.startswith("Artista:"):
                    try:
                        partes = linea.replace("Artista:", "").split(", Canción:")
                        artista = partes[0].strip()
                        cancion = partes[1].strip()
                        busqueda = f"{artista} {cancion}"
                        descargar_audio(busqueda, self.carpeta_destino, self.log)
                    except Exception as e:
                        self.log(f"❌ No se pudo procesar la línea: {linea} - {e}")
                elif linea:
                    descargar_audio(linea, self.carpeta_destino, self.log)
        except Exception as e:
            self.log(f"❌ Error al leer el archivo TXT: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DescargadorApp(root)
    root.mainloop()
