import re
import os
import winreg
import time


def remove_ansi_escape_sequences(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def get_download_folder():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        download_folder = winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
        youtube_folder = os.path.join(download_folder, 'YouTube')

        if not os.path.exists(youtube_folder):
            os.makedirs(youtube_folder)

        return youtube_folder
    except Exception as e:
        print(f"Bład przy pobieraniu ścieżki do folderu Pobrane: {e}")
        return os.path.join(os.path.expanduser("~"), "Downloads", "YouTube")

def progress_hook(d, stop_download, progress_label, size_label, progress_bar, speed_label, eta_label):
    if stop_download:
        raise Exception("Pobieranie zatrzymane przez użytkownika.")
    
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes')
        if total_bytes:
            percent = downloaded_bytes / total_bytes * 100
            progress_bar['value'] = percent
            progress_label.config(text=f"Pobieranie: {percent:.2f}%")
            size_label.config(text=f"Rozmiar: {total_bytes / 1024 / 1024:.2f} MB")
        
        speed = d.get('speed')
        if speed:
            speed_label.config(text=f"Prędkość pobierania: {speed / 1024 / 1024:.2f} MB/s")
        
        eta = d.get('eta')
        if eta:
            eta_label.config(text=f"Przewidywany czas: {time.strftime('%H:%M:%S', time.gmtime(eta))}")

    elif d['status'] == 'finished':
        progress_label.config(text="Pobieranie zakończone.")
        size_label.config(text="Plik zapisany.")
        speed_label.config(text="")
        eta_label.config(text="")