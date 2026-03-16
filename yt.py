import os
import re
import yt_dlp
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import threading


def sanitize_filename(name: str) -> str:
    """Remove characters not allowed in filenames on Windows/most OSes."""
    return re.sub(r'[<>:"/\\|?*\n\r]+', '', name).strip()

def descargar_audio(busqueda_o_url, carpeta_destino, log_callback, progress_callback, total_callback):
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
            'quiet': True,  # Silenciar para usar hooks
        }

        with yt_dlp.YoutubeDL(opciones) as ydl:
            # Obtener info para contar total
            if es_url:
                info = ydl.extract_info(busqueda_o_url, download=False)
                if 'entries' in info:
                    total = len(info['entries'])
                    total_callback(total)
                    log_callback(f"🔎 Descargando playlist con {total} canciones desde URL: {busqueda_o_url}")
                else:
                    total_callback(1)
                    log_callback(f"🔎 Descargando video desde URL: {busqueda_o_url}")
            else:
                total_callback(1)
                log_callback(f"🔎 Buscando en YouTube: {busqueda_o_url}")

            # Agregar hooks
            opciones['progress_hooks'] = [lambda d: progress_callback(d)]
            opciones['postprocessor_hooks'] = [lambda d: progress_callback(d)]

            ydl.params.update(opciones)
            ydl.download([busqueda_o_url] if es_url else [f"ytsearch1:{busqueda_o_url}"])

        log_callback(f"✅ Descarga completada.")

    except Exception as e:
        log_callback(f"❌ Error al procesar '{busqueda_o_url}': {e}")


class DescargadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de MP3 de YouTube")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Variables
        self.modo = tk.StringVar(value="manual")
        self.carpeta_destino = ""
        self.archivo_txt = ""
        self.total_canciones = 0
        self.descargadas = 0

        # Frame principal
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Modo
        ttk.Label(main_frame, text="Modo de descarga:", font=("Arial", 10, "bold")).pack(pady=5)
        frame_modo = ttk.Frame(main_frame)
        frame_modo.pack(pady=5)
        ttk.Radiobutton(frame_modo, text="Manual (URL o búsqueda)", variable=self.modo, value="manual").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(frame_modo, text="Desde archivo TXT", variable=self.modo, value="txt").pack(side=tk.LEFT, padx=10)

        # Carpeta
        ttk.Label(main_frame, text="Carpeta de destino:", font=("Arial", 10, "bold")).pack(pady=5)
        frame_carpeta = ttk.Frame(main_frame)
        frame_carpeta.pack(pady=5, fill=tk.X)
        self.lbl_carpeta = ttk.Label(frame_carpeta, text="No seleccionada", relief="sunken", padding=5)
        self.lbl_carpeta.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        ttk.Button(frame_carpeta, text="Seleccionar", command=self.seleccionar_carpeta).pack(side=tk.RIGHT)

        # Manual (siempre visible)
        ttk.Label(main_frame, text="Ingresa URL de YouTube (video o playlist) o búsqueda:", font=("Arial", 10, "bold")).pack(pady=5)
        self.entry_busqueda = ttk.Entry(main_frame, width=60)
        self.entry_busqueda.pack(pady=5, fill=tk.X)

        # TXT
        self.frame_txt = ttk.LabelFrame(main_frame, text="Archivo TXT", padding=10)
        ttk.Label(self.frame_txt, text="Archivo TXT con canciones:").pack(pady=5)
        frame_txt_sel = ttk.Frame(self.frame_txt)
        frame_txt_sel.pack(pady=5, fill=tk.X)
        self.lbl_txt = ttk.Label(frame_txt_sel, text="No seleccionado", relief="sunken", padding=5)
        self.lbl_txt.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        ttk.Button(frame_txt_sel, text="Seleccionar", command=self.seleccionar_txt).pack(side=tk.RIGHT)

        # Progreso
        frame_progreso = ttk.Frame(main_frame)
        frame_progreso.pack(pady=10, fill=tk.X)
        self.lbl_total = ttk.Label(frame_progreso, text="Canciones totales: 0")
        self.lbl_total.pack(side=tk.LEFT, padx=10)
        self.progressbar = ttk.Progressbar(frame_progreso, orient="horizontal", length=300, mode="determinate")
        self.progressbar.pack(side=tk.RIGHT, padx=10, fill=tk.X, expand=True)

        # Botones
        frame_botones = ttk.Frame(main_frame)
        frame_botones.pack(pady=10)
        ttk.Button(frame_botones, text="Iniciar Descarga", command=self.iniciar_descarga).pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_botones, text="Limpiar Logs", command=self.limpiar_logs).pack(side=tk.LEFT, padx=10)

        # Logs
        ttk.Label(main_frame, text="Logs de descarga:", font=("Arial", 10, "bold")).pack(pady=5)
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, wrap=tk.WORD, font=("Courier", 9))
        self.log_text.pack(pady=5, fill=tk.BOTH, expand=True)

        # Creador
        ttk.Label(main_frame, text="Desarrollado por Sopor", font=("Arial", 8, "italic")).pack(pady=5)

        self.modo.trace("w", self.cambiar_modo)
        self.cambiar_modo()

    def cambiar_modo(self, *args):
        if self.modo.get() == "manual":
            self.frame_txt.pack_forget()
        else:
            self.frame_txt.pack(fill=tk.X, pady=10)

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

    def total_callback(self, total):
        self.total_canciones = total
        self.lbl_total.config(text=f"Canciones totales: {total}")
        self.progressbar.config(maximum=total)
        self.descargadas = 0
        self.progressbar['value'] = 0

    def progress_callback(self, d):
        if d['status'] == 'finished':
            self.descargadas += 1
            self.progressbar['value'] = self.descargadas
            self.log(f"✅ Completado: {d.get('filename', '')}")
        elif d['status'] == 'downloading':
            self.log(f"⬇️ Descargando: {d.get('filename', '')} - {d.get('_percent_str', '0%')}")

    def limpiar_logs(self):
        self.log_text.delete(1.0, tk.END)

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
        descargar_audio(busqueda, self.carpeta_destino, self.log, self.progress_callback, self.total_callback)

    def descargar_txt(self):
        try:
            with open(self.archivo_txt, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            total_lineas = sum(1 for linea in lineas if linea.strip())
            self.total_callback(total_lineas)

            for linea in lineas:
                linea = linea.strip()
                if linea.startswith("Artista:"):
                    try:
                        partes = linea.replace("Artista:", "").split(", Canción:")
                        artista = partes[0].strip()
                        cancion = partes[1].strip()
                        busqueda = f"{artista} {cancion}"
                        descargar_audio(busqueda, self.carpeta_destino, self.log, self.progress_callback, lambda x: None)  # No cambiar total aquí
                    except Exception as e:
                        self.log(f"❌ No se pudo procesar la línea: {linea} - {e}")
                elif linea:
                    descargar_audio(linea, self.carpeta_destino, self.log, self.progress_callback, lambda x: None)
        except Exception as e:
            self.log(f"❌ Error al leer el archivo TXT: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DescargadorApp(root)
    root.mainloop()
