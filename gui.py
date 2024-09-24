import tkinter as tk
from tkinter import ttk, messagebox
from utils import is_youtube_link
from update_manager import *
import sys
import os

class YouTubeDownloaderGUI:
    def __init__(self, root, start_download_callback, stop_download_callback, check_for_updates_callback, download_update_callback):
        self.root = root
        self.current_version = "2.3" #Program  version
        self.start_download_callback = start_download_callback
        self.stop_download_callback = stop_download_callback
        self.check_for_updates_callback = check_for_updates_callback
        self.download_update_callback = download_update_callback
        self.root.title(f"YouTube Downloader")
        self.root.geometry("700x400")
        self.root.resizable(0, 0)
        self.root.config(bg='#2c3e50')
        self.init_ui()
        self.root.after(1000, self.check_clipboard)

    def init_ui(self):
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background='#ffffff', borderwidth=0)
        style.configure("TNotebook.Tab", font=("Helvetica", 12), background='#ecf0f1', foreground='#000000', padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#3498db")])
        style.configure("TLabel", font=("Helvetica", 12), background='#dcdad5', foreground='#000000')
        style.configure("TButton", font=("Helvetica", 12, 'bold'), background='#2980b9', foreground='#ffffff')
        style.map("TButton", background=[("active", "#1abc9c")])
        style.configure("TEntry", font=("Helvetica", 12), padding=[5, 5])
        style.configure("TProgressbar", thickness=20, background='#3498db')

        # Tab Control
        tab_control = ttk.Notebook(self.root)
        tab_control.pack(expand=1, fill='both')

        # Download Tab
        download_tab = ttk.Frame(tab_control, padding="10 10 10 10")
        tab_control.add(download_tab, text="Pobieranie")

        self.link_label = ttk.Label(download_tab, text="Pobierz wideo z YouTube")
        self.link_label.grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Label(download_tab, text="Wklej link tutaj =>").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.link = tk.StringVar()
        ttk.Entry(download_tab, width=50, textvariable=self.link).grid(row=1, column=1, padx=1, pady=1, sticky='w')

        self.paste_button = ttk.Button(download_tab, text="Wklej link ze schowka", command=self.paste_from_clipboard)
        self.paste_button.grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.paste_button.pack_forget()

        ttk.Label(download_tab, text="Wybierz rozdzielczość:").grid(row=2, column=0, pady=5, padx=5, sticky='w')
        self.resolutions = ["4K", "1440p", "1080p", "720p", "480p", "360p", "Tylko audio"]
        self.selected_resolution = tk.StringVar(value=self.resolutions[0])  # Domyślne ustawienie na "4K"

        self.output_formats = ["mp4", "mkv", "webm"]
        self.selected_format = tk.StringVar(value=self.output_formats[0])

        self.resolution_frame = ttk.Frame(download_tab)
        self.resolution_frame.grid(row=2, column=1, columnspan=2, pady=5, padx=5, sticky='w')

        resolution_menu = tk.OptionMenu(self.resolution_frame, self.selected_resolution, *self.resolutions)
        resolution_menu.pack(side='left')
        resolution_menu.config(width=15)

        format_menu = tk.OptionMenu(self.resolution_frame, self.selected_format, *self.output_formats)
        format_menu.pack(side='left', padx=(5, 0))
        format_menu.config(width=10)
        
        self.download_subtitles = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.resolution_frame, text="Pobierz napisy", variable=self.download_subtitles).pack(side='left', padx=(5, 0))

        button_frame = ttk.Frame(download_tab)
        button_frame.grid(column=0, row=3, columnspan=3, pady=5, sticky='w')

        self.download_button = ttk.Button(button_frame, text="Pobierz", command=self.start_download)
        self.download_button.pack(side='left')
        
        self.stop_button = ttk.Button(button_frame, text="Zatrzymaj", command=self.stop_download_callback)
        self.stop_button.pack(side='left', padx=(5, 0))
        self.stop_button.pack_forget()

        # Progress and Status
        self.progress_label = ttk.Label(download_tab, text="")
        self.progress_label.grid(column=0, row=4, columnspan=3, pady=5, sticky='w')

        self.progress_bar = ttk.Progressbar(download_tab, orient="horizontal", length=600, mode="determinate")
        self.progress_bar.grid(column=0, row=5, columnspan=3, pady=5, sticky='ew')

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

        ttk.Label(settings_tab, text="Domyślnie pobiera się do: Pobrane => YouTube").grid(column=0, row=1, columnspan=3, padx=5, pady=5, sticky='w')

        ttk.Button(settings_tab, text="Zapisz ustawienia", command=self.save_settings).grid(column=0, row=2, pady=10)

        # update tab
        update_tab = ttk.Frame(tab_control, padding="10 10 10 10")
        tab_control.add(update_tab, text="Aktualizacje/Informacje")

        ttk.Label(update_tab, text=f"Aktualna wersja: {self.current_version}").grid(column=0, row=0, padx=5, pady=5, sticky='w')
        ttk.Label(update_tab, text="Autor - snowycoldd:").grid(column=1, row=0, padx=5, pady=5, sticky='w')
        
        self.update_status_label = ttk.Label(update_tab, text="")
        self.update_status_label.grid(column=0, row=1, padx=5, pady=5, sticky='w')

        self.check_update_button = ttk.Button(update_tab, text="Sprawdź aktualizacje", command=self.check_for_updates)
        self.check_update_button.grid(column=0, row=2, padx=5, pady=5, sticky='w')

        self.update_button = ttk.Button(update_tab, text="Zainstaluj aktualizację", command=self.download_update_callback)
        self.update_button.grid(column=0, row=3, padx=5, pady=5, sticky='w')
        self.update_button.grid_remove()

    def check_for_updates(self):
        self.check_for_updates_callback()

    def show_update_dialog(self, update_info):
        dialog = tk.Toplevel(self.root)
        dialog.title("Dostępna aktualizacja")
        dialog.geometry("500x400")
        dialog.resizable(0, 0)

        ttk.Label(dialog, text=f"Nowa wersja: {update_info.version}", font=("Helvetica", 14)).pack(pady=10)
        
        release_notes_text = tk.Text(dialog, wrap="word", width=60, height=10)
        release_notes_text.insert("1.0", update_info.release_notes)
        release_notes_text.config(state="disabled")
        release_notes_text.pack(pady=10)

        def on_download():
            dialog.destroy()
            downloaded_file = self.download_update_callback(update_info)
            if downloaded_file:
                messagebox.showinfo("Aktualizacja", f"Aktualizacja pobrana: {downloaded_file}")
                self.root.quit()
                self.root.destroy()
                os.remove(sys.argv[0])

        ttk.Button(dialog, text="Pobierz", command=on_download).pack(pady=10)
        ttk.Button(dialog, text="Anuluj", command=dialog.destroy).pack()

        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)


    def paste_from_clipboard(self):
        clipboard_content = self.root.clipboard_get()
        self.link.set(clipboard_content)
    
    def check_clipboard(self):
        try:
            clipboard_content = self.root.clipboard_get()
            if is_youtube_link(clipboard_content):
                self.paste_button.grid(row=1, column=2, padx=5, pady=5)
                self.link_label.config(text="Link YouTube wykryty w schowku!")
                self.link_label.grid(row=0, column=0, columnspan=3, pady=10)
            else:
                self.paste_button.grid_remove()
                self.link_label.config(text="Pobierz wideo z YouTube")
                self.link_label.grid(row=0, column=0, columnspan=3, pady=10)
        except:
            self.paste_button.grid_remove()
            self.link_label.config(text="Pobierz wideo z YouTube")
            self.link_label.grid(row=0, column=0, columnspan=3, pady=10)
        self.root.after(1000, self.check_clipboard)


    def start_download(self):
        url = self.link.get()
        resolution = self.selected_resolution.get()
        download_subtitles = self.download_subtitles.get()
        output_format = self.selected_format.get()
        subtitle_language = None

        if not url.strip():
            messagebox.showerror("Błąd", "Proszę wprowadzić link przed rozpoczęciem pobierania.")
        else:
            if download_subtitles:
                subtitle_language = self.show_subtitles_language_dialog()
                if subtitle_language:
                    self.start_download_callback(url, resolution, download_subtitles, output_format, subtitle_language)
                    self.stop_button.pack()
            else:
                self.start_download_callback(url, resolution, download_subtitles, output_format, subtitle_language)
                self.stop_button.pack()

    
    def show_subtitles_language_dialog(self):
        languages = ["pl", "en", "de", "fr", "es"]
        language = tk.StringVar(value=languages[0])

        dialog = tk.Toplevel(self.root)
        dialog.title("Wybór języka napisów")
        dialog.geometry("400x300")
        dialog.resizable(0, 0) 

        ttk.Label(dialog, text="Wybierz język napisów:").pack(pady=10)
        language_menu = tk.OptionMenu(dialog, language, *languages)
        language_menu.pack(pady=10)

        info_text = "Uwaga: Proces zapisywania filmu z napisami może wymagać\n" \
                    "znacznie dłuższego czasu niż w przypadku filmu bez napisów.\n" \
                    "Czas przetwarzania jest proporcjonalny do długości filmu."
        ttk.Label(dialog, text=info_text, wraplength=350, justify="center").pack(pady=10)
        
        def on_ok():
            dialog.destroy()

        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=10)

        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
    
        return language.get()

    def save_settings(self):
        messagebox.showinfo("Ustawienia", "Ustawienia zostały zapisane.")

    def show_message(self, title, message):
        messagebox.showinfo(title, message)