import tkinter as tk
from tkinter import ttk, messagebox

class YouTubeDownloaderGUI:
    def __init__(self, root, start_download_callback, stop_download_callback):
        self.root = root
        self.start_download_callback = start_download_callback
        self.stop_download_callback = stop_download_callback
        self.init_ui()

    def init_ui(self):
        self.root.title("YouTube Downloader 2.0")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.config(bg='#2c3e50')

        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background='#ffffff', borderwidth=0)
        style.configure("TNotebook.Tab", font=("Helvetica", 12), background='#ecf0f1', foreground='#000000', padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#3498db")])
        style.configure("TLabel", font=("Helvetica", 12), background='#dcdad5', foreground='#000000')
        style.configure("TButton", font=("Helvetica", 12, 'bold'), background='#2980b9', foreground='#ffffff')
        style.map("TButton", background=[("active", "#1abc9c")])  # Hover effect
        style.configure("TEntry", font=("Helvetica", 12), padding=[5, 5])
        style.configure("TProgressbar", thickness=20, background='#3498db')

        # Tab Control
        tab_control = ttk.Notebook(self.root)
        tab_control.pack(expand=1, fill='both')

        # Download Tab
        download_tab = ttk.Frame(tab_control, padding="10 10 10 10")
        tab_control.add(download_tab, text="Pobieranie")

        ttk.Label(download_tab, text="Pobierz wideo z YouTube").grid(column=0, row=0, columnspan=3, pady=10)

        ttk.Label(download_tab, text="Wklej link tutaj:").grid(column=0, row=1, padx=5, pady=5, sticky='w')
        self.link = tk.StringVar()
        ttk.Entry(download_tab, width=40, textvariable=self.link).grid(column=1, row=1, columnspan=2, padx=5, pady=5)

        ttk.Label(download_tab, text="Wybierz rozdzielczość:").grid(column=0, row=2, padx=5, pady=5, sticky='w')
        self.resolutions = ["4K", "1440p", "1080p", "720p", "480p", "360p", "Tylko audio"]
        self.selected_resolution = tk.StringVar(value=self.resolutions[0])  # Domyślne ustawienie na "4K"

        # Użycie tk.OptionMenu zamiast ttk.OptionMenu
        resolution_menu = tk.OptionMenu(download_tab, self.selected_resolution, *self.resolutions)
        resolution_menu.grid(column=1, row=2, padx=5, pady=5)
        resolution_menu.config(width=15)  # Opcjonalnie: ustawienie szerokości menu

        ttk.Button(download_tab, text="Pobierz", command=self.start_download).grid(column=0, row=3, pady=10)
        self.stop_button = ttk.Button(download_tab, text="Zatrzymaj", command=self.stop_download_callback)
        self.stop_button.grid(column=1, row=3, pady=10)
        self.stop_button.grid_remove()

        # Progress and Status
        self.progress_label = ttk.Label(download_tab, text="")
        self.progress_label.grid(column=0, row=4, columnspan=3, pady=5, sticky='w')

        self.progress_bar = ttk.Progressbar(download_tab, orient="horizontal", length=450, mode="determinate")
        self.progress_bar.grid(column=0, row=5, columnspan=3, pady=5)

        self.size_label = ttk.Label(download_tab, text="")
        self.size_label.grid(column=0, row=6, columnspan=3, pady=5, sticky='w')
    
        self.speed_label = ttk.Label(download_tab, text="")
        self.speed_label.grid(column=0, row=7, columnspan=3, pady=5, sticky='w')

        self.eta_label = ttk.Label(download_tab, text="")
        self.eta_label.grid(column=0, row=8, columnspan=3, pady=5, sticky='w')

        # Settings Tab
        settings_tab = ttk.Frame(tab_control, padding="10 10 10 10")
        tab_control.add(settings_tab, text="Ustawienia")

        ttk.Label(settings_tab, text="Ścieżka pobierania:").grid(column=0, row=0, padx=5, pady=5, sticky='w')
        self.download_path = tk.StringVar(value="/default/path")
        ttk.Entry(settings_tab, width=40, textvariable=self.download_path).grid(column=1, row=0, columnspan=2, padx=5, pady=5)

        ttk.Button(settings_tab, text="Zapisz ustawienia", command=self.save_settings).grid(column=0, row=1, pady=10)

    def start_download(self):
        url = self.link.get()
        resolution = self.selected_resolution.get()
        if not url.strip():
            messagebox.showerror("Błąd", "Proszę wprowadzić link przed rozpoczęciem pobierania.")
        else:
            self.start_download_callback(url, resolution)
            self.stop_button.grid()

    def save_settings(self):
        # Implementacja zapisywania ustawień
        messagebox.showinfo("Ustawienia", "Ustawienia zostały zapisane.")

    def show_message(self, title, message):
        messagebox.showinfo(title, message)
