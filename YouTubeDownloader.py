import threading
import tkinter as tk
from tkinter import ttk, messagebox
from yt_dlp import YoutubeDL
import re
import os 
import winreg

def remove_ansi_escape_sequences(text):
    ansi_escape = re.compile(r'\x1b\[([0-9]+)(;[0-9]+)*m')
    return ansi_escape.sub('', text)

def get_download_folder():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        download_folder = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
        youtube_folder = os.path.join(download_folder, "YouTube")
        
        if not os.path.exists(youtube_folder):
            os.makedirs(youtube_folder)
        
        return youtube_folder
    except Exception as e:
        print(f"Błąd przy pobieraniu ścieżki do folderu Pobrane: {e}")
        return os.path.join(os.path.expanduser("~"), "Downloads", "YouTube")

def progress_hook(d):
    if d['status'] == 'downloading':
        percent_str = remove_ansi_escape_sequences(d['_percent_str']).strip('%')
        progress_label.config(text=f"Pobieranie: {percent_str}% ukończono")
        if d.get('_total_bytes_str'):
            size_label.config(text=f"Szacowany rozmiar: {d['_total_bytes_str']}")
        progress_bar['value'] = float(percent_str)
    elif d['status'] == 'finished':
        progress_label.config(text="Pobieranie zakończone!")
        size_label.config(text="Plik zapisany.")


def start_download():
    url = link.get()
    if not url.strip():
        messagebox.showerror("Błąd", "Proszę wprowadzić link przed rozpoczęciem pobierania.")
        return
    
    selected_resolution_text = selected_resolution.get()

    if selected_resolution_text == "Najwyższa":
        selected_resolution_text = "bestvideo+bestaudio/best"
    else:
        selected_resolution_text = f'bestvideo[height<={selected_resolution_text[:-1]}]+bestaudio/best'

    progress_bar['value'] = 0
    progress_label.config(text="Rozpoczynanie pobierania...")
    size_label.config(text="Szacowany rozmiar: Nieznany")

    download_thread = threading.Thread(target=download_video, args=(url, selected_resolution_text))
    download_thread.start()

stop_download = False

def stop_download_function():
    global stop_download
    stop_download = True
    stop_button.place_forget()
    progress_label.config(text="Pobieranie zatrzymane.")

def download_video(url, selected_resolution_text):
    global stop_download
    stop_download = False

    download_folder = get_download_folder()
    ydl_opts = {
        'format': selected_resolution_text,
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            if stop_download:
                progress_label.config(text="Pobieranie zatrzymane.")
            else:
                progress_label.config(text=f"Błąd podczas pobierania: {e}")

root = tk.Tk()
root.title("YouTube Downloader 1.2")
root.geometry("500x400")
root.resizable(0, 0)
root.config(bg='#e6f2ff')

style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 12), background='#e6f2ff', foreground='black')
style.configure("TButton", font=("Helvetica", 12, 'bold'), backgrond='#e6f2ff', foreground='black', focuscolor='none')
style.configure("TEntry", font=("Helvetica", 12))
style.configure("TOptionMneu", font=("Helvetica", 12), backgrond='#e6f2ff', foreground='black')
style.configure("TProgressbar", thickness=20)

tk.Label(root, text="Pobieranie filmów z YouTube", font='Helvetica 16 bold', bg='#e6f2ff').pack(pady=10)
link = tk.StringVar()
tk.Label(root, text="Wklej link tutaj:", font='Helvetica 14', bg='#e6f2ff').place(x=30, y=55)
link_enter = ttk.Entry(root, width=50, textvariable=link).place(x=30, y=85)

ttk.Button(root, text='Pobierz', command=start_download).place(x=200, y=150)

stop_button = ttk.Button(root, text='Zatrzymaj', command=stop_download_function)
stop_button.place(x=300, y=150)
stop_button.place_forget()

# okno od wybierania rozdzielczości pobieraniego filmu
resolution = ["Najwyższa", "1080p", "720p", "480p", "360p"]
selected_resolution = tk.StringVar(root)
selected_resolution.set(resolution[0])  # domyślna najwyższa rozdzielczość

ttk.Label(root, text="Wybierz rozdzielczość:").place(x=30, y=210)
resolution_dropdown = tk.OptionMenu(root, selected_resolution, *resolution)
resolution_dropdown.place(x=200, y=208)

progress_label = tk.Label(root, text="", font='Helvetica 12', bg='#e6f2ff', fg='black')
progress_label.place(x=30, y=250)

size_label = tk.Label(root, text="Szaczowany czas: Nieznazy", font='Helvetica 12', bg='#e6f2ff', fg='black')
size_label.place(x=30, y=290)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.place(x=30, y=320)

root.mainloop()