import threading
import tkinter as tk
from tkinter import ttk, messagebox
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import re
import os
import winreg
import time

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
    global progress_label, size_label, progress_bar, speed_label, eta_label
    if stop_download:
        raise Exception("Pobieranie zatrzymane przez użytkownika.")

    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes')
        if total_bytes:
            percent = downloaded_bytes / total_bytes * 100
            progress_bar['value'] = percent
            progress_label.config(text=f"Pobieranie: {percent:.2f}%")
            size_label.config(text=f"Rozmiar: {total_bytes / (1024 * 1024):.2f} MB")
        
        speed = d.get('speed')
        if speed:
            speed_label.config(text=f"Prędkość: {speed / (1024 * 1024):.2f} MB/s")
        
        eta = d.get('eta')
        if eta:
            eta_label.config(text=f"Przewidywany czas: {time.strftime('%H:%M:%S', time.gmtime(eta))}")

    elif d['status'] == 'finished':
        progress_label.config(text="Pobieranie zakończone!")
        size_label.config(text="Plik zapisany.")
        speed_label.config(text="")
        eta_label.config(text="")

download_queue = []

def start_download():
    url = link.get()
    if not url.strip():
        messagebox.showerror("Błąd", "Proszę wprowadzić link przed rozpoczęciem pobierania.")
        return
    
    download_queue.append((url, selected_resolution.get()))
    if len(download_queue) == 1:
        process_queue()
        stop_button.place(x=300, y=150)
    else:
        messagebox.showinfo("Informacja", "Link dodany do kolejki pobierań.")

def process_queue():
    if download_queue:
        url, resolution = download_queue[0]
        download_thread = threading.Thread(target=download_video, args=(url, resolution))
        download_thread.start()
    else:
        messagebox.showinfo("Informacja", "Wszystkie pobierania zakończone.")

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
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        },
    }

    if selected_resolution_text == "Tylko audio":
        ydl_opts['format'] = "bestaudio/best"
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        resolution_map = {
            "4K": "2160",
            "1440p": "1440",
            "1080p": "1080",
            "720p": "720",
            "480p": "480",
            "360p": "360"
        }
        selected_res = resolution_map.get(selected_resolution_text, "best")
        ydl_opts['format'] = f'bestvideo[height<={selected_res}]+bestaudio/best[height<={selected_res}]'

    with YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except DownloadError as e:
            error_message = str(e)
            if "Requested format is not available" in error_message:
                messagebox.showwarning("Ostrzeżenie", "Wybrany format nie jest dostępny. Spróbuj innej rozdzielczości.")
            else:
                messagebox.showerror("Błąd", f"Wystąpił błąd podczas pobierania: {error_message}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nieoczekiwany błąd: {str(e)}")
        finally:
            download_queue.pop(0)
            root.after(1000, process_queue)
root = tk.Tk()
root.title("YouTube Downloader 1.4")
root.geometry("500x500")
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

resolution = ["4K", "1440p", "1080p", "720p", "480p", "360p", "Tylko audio"]
selected_resolution = tk.StringVar(root)
selected_resolution.set(resolution[0])

ttk.Label(root, text="Wybierz rozdzielczość:").place(x=30, y=210)
resolution_dropdown = tk.OptionMenu(root, selected_resolution, *resolution)
resolution_dropdown.place(x=200, y=208)

progress_label = tk.Label(root, text="", font='Helvetica 12', bg='#e6f2ff', fg='black')
progress_label.place(x=30, y=250)

size_label = tk.Label(root, text="", font='Helvetica 12', bg='#e6f2ff', fg='black')
size_label.place(x=30, y=290)

speed_label = tk.Label(root, text="", font='Helvetica 12', bg='#e6f2ff', fg='black')
speed_label.place(x=30, y=330)

eta_label = tk.Label(root, text="", font='Helvetica 12', bg='#e6f2ff', fg='black')
eta_label.place(x=30, y=370)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.place(x=30, y=410)

root.mainloop()
